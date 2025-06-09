import asyncio
import json
from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, Set
from app.prompts import Obligation_Prompt
from app.utils.logger import ColorLogger as log

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

BATCH_SIZE = 5  # Process 5 chunks at a time
MAX_RETRIES = 3

class ObligationTracker:
    def __init__(self):
        self.seen_obligations: Set[str] = set()
        self.party_names: Dict[str, str] = {}

    def is_duplicate(self, obligation_text: str) -> bool:
        """Check if an obligation is duplicate based on its text"""
        text_hash = hash(obligation_text.lower().strip())
        if text_hash in self.seen_obligations:
            return True
        self.seen_obligations.add(text_hash)
        return False

    def standardize_party_name(self, name: str) -> str:
        """Standardize party name to maintain consistency"""
        key = name.lower().strip()
        if key not in self.party_names:
            # Store the first occurrence in Title Case
            self.party_names[key] = name.title()
        return self.party_names[key]

async def process_chunk(chunk: Dict[str, str], tracker: ObligationTracker) -> Dict:
    log.chunk(f"Processing chunk from section {chunk['section_number']} (Page {chunk['page_number']})")
    
    for attempt in range(MAX_RETRIES):
        try:
            # Add context to the chunk content
            content_with_context = f"Context: {chunk['context']}\n\nContent:\n{chunk['text']}"
            
            log.processing(f"Sending to OpenAI (Attempt {attempt + 1}/{MAX_RETRIES})", indent=1)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {"role": "system", "content": Obligation_Prompt.SYSTEM_PROMPT},
                    {"role": "user", "content": content_with_context}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content.strip().lower() != "null":
                result = json.loads(content)
                
                # Process each party's obligations
                if "parties" in result:
                    for party in result["parties"]:
                        # Standardize party name
                        original_name = party["name"]
                        party["name"] = tracker.standardize_party_name(party["name"])
                        if original_name != party["name"]:
                            log.party(f"Standardized party name: {original_name} → {party['name']}", indent=1)
                        
                        # Filter out duplicate obligations
                        if "obligations" in party:
                            original_count = len(party["obligations"])
                            party["obligations"] = [
                                {**ob, "section": chunk["section_number"]}
                                for ob in party["obligations"]
                                if not tracker.is_duplicate(ob["obligation_text"])
                            ]
                            filtered_count = len(party["obligations"])
                            
                            if filtered_count > 0:
                                log.obligation(f"Found {filtered_count} new obligations for {party['name']}", indent=1)
                            if original_count > filtered_count:
                                log.warning(f"Filtered out {original_count - filtered_count} duplicate obligations", indent=2)
                
                log.success(f"Successfully processed chunk", indent=1)
                return result
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error processing chunk after {MAX_RETRIES} attempts: {e}")
            await asyncio.sleep(1)  # Back off before retry
    return None

async def extract_obligation_from_chunks(chunks: List[Dict[str, str]]) -> List[Dict]:
    log.info(f"🚀 Starting obligation extraction for {len(chunks)} chunks")
    results = []
    tracker = ObligationTracker()
    
    # Process chunks in batches
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(chunks), BATCH_SIZE):
        current_batch = i // BATCH_SIZE + 1
        batch = chunks[i:i + BATCH_SIZE]
        log.processing(f"Processing batch {current_batch}/{total_batches} ({len(batch)} chunks)")
        
        tasks = [process_chunk(chunk, tracker) for chunk in batch]
        batch_results = await asyncio.gather(*tasks)
        
        # Filter out None results and extend the results list
        valid_results = [r for r in batch_results if r is not None]
        results.extend(valid_results)
        
        log.success(f"Completed batch {current_batch}/{total_batches} with {len(valid_results)} valid results")
        
        # Add a small delay between batches to avoid rate limits
        if i + BATCH_SIZE < len(chunks):
            log.info("Waiting before next batch to avoid rate limits...", indent=1)
            await asyncio.sleep(0.5)
    
    # Merge results by party
    log.processing("Merging results by party...")
    merged_results = {}
    total_obligations = 0
    
    for result in results:
        if "parties" in result:
            for party in result["parties"]:
                party_name = party["name"]
                if party_name not in merged_results:
                    merged_results[party_name] = {
                        "name": party_name,
                        "obligations": []
                    }
                merged_results[party_name]["obligations"].extend(party["obligations"])
                total_obligations += len(party["obligations"])
    
    log.success(f"✨ Extraction complete! Found {total_obligations} obligations across {len(merged_results)} parties")
    
    return [{"parties": list(merged_results.values())}]
            
                
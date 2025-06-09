import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import DocumentUpload from './pages/DocumentUpload'
import ObligationsList from './pages/ObligationsList'
import ObligationEdit from './pages/ObligationEdit'
import { ObligationProvider } from './context/ObligationContext'

const App = () => {
  return (
    <ObligationProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<DocumentUpload />} />
              <Route path="/obligations" element={<ObligationsList />} />
              <Route path="/obligations/:id" element={<ObligationEdit />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ObligationProvider>
  )
}

export default App
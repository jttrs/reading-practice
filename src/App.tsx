import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import DecodingModule from './modules/decoding/DecodingModule'
import SightWordsModule from './modules/sight-words/SightWordsModule'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/decoding" element={<DecodingModule />} />
      <Route path="/sight-words" element={<SightWordsModule />} />
    </Routes>
  )
}

import { useState, useEffect } from 'react'
import CollectionList from './components/CollectionList'
import CollectionManager from './components/CollectionManager'
import PipelineRunner from './components/PipelineRunner'
import LLMConfig from './components/LLMConfig'
import { Collection } from './types'

function App() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null)
  const [activeTab, setActiveTab] = useState<'collections' | 'pipeline' | 'config'>('collections')

  useEffect(() => {
    fetchCollections()
  }, [])

  const fetchCollections = async () => {
    try {
      const response = await fetch('/api/collections')
      const data = await response.json()
      setCollections(data)
    } catch (error) {
      console.error('Failed to fetch collections:', error)
    }
  }

  return (
    <div>
      <h1>Collectivist</h1>
      
      <nav>
        <button onClick={() => setActiveTab('collections')}>Collections</button>
        <button onClick={() => setActiveTab('pipeline')}>Pipeline</button>
        <button onClick={() => setActiveTab('config')}>Configuration</button>
      </nav>

      {activeTab === 'collections' && (
        <div>
          <h2>Collections</h2>
          <CollectionList 
            collections={collections}
            onSelect={setSelectedCollection}
            onRefresh={fetchCollections}
          />
          <CollectionManager 
            selectedCollection={selectedCollection}
            onUpdate={fetchCollections}
          />
        </div>
      )}

      {activeTab === 'pipeline' && (
        <div>
          <h2>Pipeline Runner</h2>
          <PipelineRunner 
            collections={collections}
            selectedCollection={selectedCollection}
            onSelectCollection={setSelectedCollection}
          />
        </div>
      )}

      {activeTab === 'config' && (
        <div>
          <h2>Configuration</h2>
          <LLMConfig />
        </div>
      )}
    </div>
  )
}

export default App
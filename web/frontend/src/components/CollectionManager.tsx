import { useState } from 'react'
import { Collection } from '../types'

interface CollectionManagerProps {
  selectedCollection: Collection | null
  onUpdate: () => void
}

export default function CollectionManager({ selectedCollection, onUpdate }: CollectionManagerProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [newCollection, setNewCollection] = useState({
    name: '',
    path: '',
    force_type: ''
  })

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/collections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCollection.name,
          path: newCollection.path,
          force_type: newCollection.force_type || undefined
        })
      })
      
      if (response.ok) {
        setNewCollection({ name: '', path: '', force_type: '' })
        setIsCreating(false)
        onUpdate()
      } else {
        const error = await response.json()
        alert(`Failed to create collection: ${error.detail}`)
      }
    } catch (error) {
      alert(`Failed to create collection: ${error}`)
    }
  }

  const handleDelete = async (collectionId: string) => {
    if (!confirm('Are you sure you want to delete this collection?')) return
    
    try {
      const response = await fetch(`/api/collections/${collectionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        onUpdate()
      } else {
        const error = await response.json()
        alert(`Failed to delete collection: ${error.detail}`)
      }
    } catch (error) {
      alert(`Failed to delete collection: ${error}`)
    }
  }

  return (
    <div>
      <h3>Collection Management</h3>
      
      <button onClick={() => setIsCreating(!isCreating)}>
        {isCreating ? 'Cancel' : 'Add Collection'}
      </button>

      {isCreating && (
        <form onSubmit={handleCreate}>
          <div>
            <label>Name:</label>
            <input
              type="text"
              value={newCollection.name}
              onChange={(e) => setNewCollection({...newCollection, name: e.target.value})}
              required
            />
          </div>
          <div>
            <label>Path:</label>
            <input
              type="text"
              value={newCollection.path}
              onChange={(e) => setNewCollection({...newCollection, path: e.target.value})}
              required
            />
          </div>
          <div>
            <label>Force Type (optional):</label>
            <select
              value={newCollection.force_type}
              onChange={(e) => setNewCollection({...newCollection, force_type: e.target.value})}
            >
              <option value="">Auto-detect</option>
              <option value="repositories">Repositories</option>
              <option value="media">Media</option>
              <option value="documents">Documents</option>
            </select>
          </div>
          <button type="submit">Create Collection</button>
        </form>
      )}

      {selectedCollection && (
        <div>
          <h4>Selected Collection</h4>
          <div>ID: {selectedCollection.id}</div>
          <div>Name: {selectedCollection.name}</div>
          <div>Path: {selectedCollection.path}</div>
          <div>Type: {selectedCollection.collection_type}</div>
          <div>Status: {selectedCollection.status}</div>
          <button onClick={() => handleDelete(selectedCollection.id)}>
            Delete Collection
          </button>
        </div>
      )}
    </div>
  )
}
import { Collection } from '../types'

interface CollectionListProps {
  collections: Collection[]
  onSelect: (collection: Collection) => void
  onRefresh: () => void
}

export default function CollectionList({ collections, onSelect, onRefresh }: CollectionListProps) {
  return (
    <div>
      <h3>Collections</h3>
      <button onClick={onRefresh}>Refresh</button>
      
      <ul>
        {collections.map(collection => (
          <li key={collection.id}>
            <button onClick={() => onSelect(collection)}>
              {collection.name} ({collection.collection_type}) - {collection.status}
            </button>
            <div>Path: {collection.path}</div>
            <div>Categories: {collection.categories.join(', ')}</div>
            {collection.last_scan && <div>Last scan: {collection.last_scan}</div>}
          </li>
        ))}
      </ul>
    </div>
  )
}
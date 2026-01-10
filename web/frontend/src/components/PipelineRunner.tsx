import { useState, useEffect } from 'react'
import { Collection, PipelineRun, PipelineRunRequest, PipelineEvent } from '../types'

interface PipelineRunnerProps {
  collections: Collection[]
  selectedCollection: Collection | null
  onSelectCollection: (collection: Collection | null) => void
}

export default function PipelineRunner({ collections, selectedCollection, onSelectCollection }: PipelineRunnerProps) {
  const [runConfig, setRunConfig] = useState<PipelineRunRequest>({
    skip_analyze: false,
    skip_scan: false,
    skip_describe: false,
    skip_readme: false,
    skip_process_new: false,
    auto_file: false,
    confidence_threshold: 0.7,
    workflow_mode: 'manual'
  })
  const [currentRun, setCurrentRun] = useState<PipelineRun | null>(null)
  const [events, setEvents] = useState<PipelineEvent[]>([])

  useEffect(() => {
    // Connect to WebSocket for real-time updates using proxy
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    const websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
    }
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'pipeline_event' && data.event) {
          setEvents(prev => [...prev, data.event])
        } else if (data.type === 'pipeline_complete') {
          setCurrentRun(prev => prev ? {...prev, status: 'completed'} : null)
        } else if (data.type === 'pipeline_error') {
          setCurrentRun(prev => prev ? {...prev, status: 'failed', error: data.error} : null)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    return () => {
      websocket.close()
    }
  }, [])

  const handleRun = async () => {
    if (!selectedCollection) {
      alert('Please select a collection first')
      return
    }

    try {
      const response = await fetch(`/api/collections/${selectedCollection.id}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runConfig)
      })

      if (response.ok) {
        const run = await response.json()
        setCurrentRun(run)
        setEvents([]) // Clear previous events
      } else {
        const error = await response.json()
        alert(`Failed to start pipeline: ${error.detail}`)
      }
    } catch (error) {
      alert(`Failed to start pipeline: ${error}`)
    }
  }

  const handleCollectionSelect = (collectionId: string) => {
    if (collectionId === '') {
      onSelectCollection(null)
    } else {
      const collection = collections.find(c => c.id === collectionId)
      onSelectCollection(collection || null)
    }
  }

  return (
    <div>
      <h3>Pipeline Runner</h3>
      
      <div>
        <h4>Collection Selection</h4>
        <select 
          value={selectedCollection?.id || ''}
          onChange={(e) => handleCollectionSelect(e.target.value)}
        >
          <option value="">Select a collection</option>
          {collections.map(collection => (
            <option key={collection.id} value={collection.id}>
              {collection.name} ({collection.status})
            </option>
          ))}
        </select>
        
        {selectedCollection && (
          <div>
            <p>Selected: {selectedCollection.name}</p>
            <p>Path: {selectedCollection.path}</p>
            <p>Type: {selectedCollection.collection_type}</p>
            <p>Status: {selectedCollection.status}</p>
          </div>
        )}
      </div>

      <div>
        <h4>Pipeline Configuration</h4>
        
        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.skip_analyze}
              onChange={(e) => setRunConfig({...runConfig, skip_analyze: e.target.checked})}
            />
            Skip Analyze
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.skip_scan}
              onChange={(e) => setRunConfig({...runConfig, skip_scan: e.target.checked})}
            />
            Skip Scan
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.skip_describe}
              onChange={(e) => setRunConfig({...runConfig, skip_describe: e.target.checked})}
            />
            Skip Describe
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.skip_readme}
              onChange={(e) => setRunConfig({...runConfig, skip_readme: e.target.checked})}
            />
            Skip README
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.skip_process_new}
              onChange={(e) => setRunConfig({...runConfig, skip_process_new: e.target.checked})}
            />
            Skip Process New
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={runConfig.auto_file}
              onChange={(e) => setRunConfig({...runConfig, auto_file: e.target.checked})}
            />
            Auto File
          </label>
        </div>

        <div>
          <label>
            Confidence Threshold:
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={runConfig.confidence_threshold}
              onChange={(e) => setRunConfig({...runConfig, confidence_threshold: parseFloat(e.target.value)})}
            />
          </label>
        </div>

        <div>
          <label>
            Workflow Mode:
            <select
              value={runConfig.workflow_mode}
              onChange={(e) => setRunConfig({...runConfig, workflow_mode: e.target.value as any})}
            >
              <option value="manual">Manual</option>
              <option value="scheduled">Scheduled</option>
              <option value="organic">Organic</option>
            </select>
          </label>
        </div>

        <button 
          onClick={handleRun} 
          disabled={!selectedCollection || selectedCollection.status !== 'idle'}
        >
          {selectedCollection?.status === 'idle' ? 'Run Pipeline' : `Collection is ${selectedCollection?.status}`}
        </button>
      </div>

      {currentRun && (
        <div>
          <h4>Current Run</h4>
          <div>Run ID: {currentRun.run_id}</div>
          <div>Status: {currentRun.status}</div>
          <div>Started: {new Date(currentRun.started_at).toLocaleString()}</div>
          {currentRun.completed_at && <div>Completed: {new Date(currentRun.completed_at).toLocaleString()}</div>}
          {currentRun.error && <div style={{color: 'red'}}>Error: {currentRun.error}</div>}
        </div>
      )}

      {events.length > 0 && (
        <div>
          <h4>Pipeline Events ({events.length})</h4>
          <div style={{maxHeight: '300px', overflow: 'auto', border: '1px solid #ccc', padding: '10px'}}>
            {events.slice(-20).map((event, index) => (
              <div key={index} style={{marginBottom: '5px'}}>
                <strong>[{event.level.toUpperCase()}]</strong> {event.stage}: {event.message}
                {event.progress_total > 0 && (
                  <span> ({event.progress_current}/{event.progress_total} - {Math.round(event.percent)}%)</span>
                )}
                <div style={{fontSize: '0.8em', color: '#666'}}>
                  {new Date(event.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
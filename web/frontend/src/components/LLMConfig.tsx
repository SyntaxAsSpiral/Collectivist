import { useState, useEffect } from 'react'
import { LLMConfig as LLMConfigType, LLMProvider } from '../types'

export default function LLMConfig() {
  const [config, setConfig] = useState<LLMConfigType>({
    provider: 'openrouter',
    api_key: '',
    base_url: '',
    model: '',
    temperature: 0.1,
    max_tokens: 2000
  })
  const [providers, setProviders] = useState<Record<string, LLMProvider>>({})
  const [testResult, setTestResult] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchConfig()
    fetchProviders()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/config/llm')
      const data = await response.json()
      setConfig(data)
    } catch (error) {
      console.error('Failed to fetch LLM config:', error)
    }
  }

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/config/llm/providers')
      const data = await response.json()
      setProviders(data)
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    }
  }

  const handleSave = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/config/llm', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })

      if (response.ok) {
        setTestResult('Configuration saved successfully')
      } else {
        const error = await response.json()
        setTestResult(`Failed to save: ${error.detail}`)
      }
    } catch (error) {
      setTestResult(`Failed to save: ${error}`)
    }
    setIsLoading(false)
  }

  const handleTest = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/config/llm/test', {
        method: 'POST'
      })

      const result = await response.json()
      if (response.ok) {
        setTestResult(`✓ Connection successful: ${result.message}`)
      } else {
        setTestResult(`✗ Connection failed: ${result.detail}`)
      }
    } catch (error) {
      setTestResult(`✗ Connection failed: ${error}`)
    }
    setIsLoading(false)
  }

  const selectedProvider = providers[config.provider]

  return (
    <div>
      <h3>LLM Configuration</h3>

      <div>
        <label>
          Provider:
          <select
            value={config.provider}
            onChange={(e) => {
              const provider = e.target.value
              const providerInfo = providers[provider]
              setConfig({
                ...config,
                provider,
                base_url: providerInfo?.base_url || '',
                model: providerInfo?.models?.[0] || ''
              })
            }}
          >
            {Object.entries(providers).map(([key, provider]) => (
              <option key={key} value={key}>
                {provider.name} - {provider.description}
              </option>
            ))}
          </select>
        </label>
      </div>

      {selectedProvider?.requires_api_key && (
        <div>
          <label>
            API Key:
            <input
              type="password"
              value={config.api_key || ''}
              onChange={(e) => setConfig({...config, api_key: e.target.value})}
              placeholder="Enter your API key"
            />
          </label>
        </div>
      )}

      <div>
        <label>
          Base URL:
          <input
            type="text"
            value={config.base_url || ''}
            onChange={(e) => setConfig({...config, base_url: e.target.value})}
            placeholder="API endpoint URL"
          />
        </label>
      </div>

      <div>
        <label>
          Model:
          <select
            value={config.model || ''}
            onChange={(e) => setConfig({...config, model: e.target.value})}
          >
            <option value="">Select a model</option>
            {selectedProvider?.models.map(model => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div>
        <label>
          Temperature:
          <input
            type="number"
            min="0"
            max="2"
            step="0.1"
            value={config.temperature || 0.1}
            onChange={(e) => setConfig({...config, temperature: parseFloat(e.target.value)})}
          />
        </label>
      </div>

      <div>
        <label>
          Max Tokens:
          <input
            type="number"
            min="1"
            max="8000"
            value={config.max_tokens || 2000}
            onChange={(e) => setConfig({...config, max_tokens: parseInt(e.target.value)})}
          />
        </label>
      </div>

      <div>
        <button onClick={handleSave} disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Configuration'}
        </button>
        <button onClick={handleTest} disabled={isLoading}>
          {isLoading ? 'Testing...' : 'Test Connection'}
        </button>
      </div>

      {testResult && (
        <div>
          <h4>Test Result</h4>
          <pre>{testResult}</pre>
        </div>
      )}
    </div>
  )
}
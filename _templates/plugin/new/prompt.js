module.exports = [
  {
    type: 'input',
    name: 'name',
    message: 'Plugin name (e.g., repositories, obsidian, media):'
  },
  {
    type: 'input',
    name: 'className',
    message: 'Class name (e.g., RepositoryScanner, ObsidianScanner):'
  },
  {
    type: 'input',
    name: 'description',
    message: 'Plugin description:'
  },
  {
    type: 'input',
    name: 'categories',
    message: 'Default categories (comma-separated, e.g., ai_llm_agents, dev_tools, utilities_misc):'
  },
  {
    type: 'input',
    name: 'supportedTypes',
    message: 'Supported item types (comma-separated, e.g., dir, file):',
    default: 'dir'
  }
]
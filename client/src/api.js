const AREAS = ['front-end', 'back-end', 'testing']
const FILES = ['instructions.md', 'completed_instructions.md']

const DEFAULT_PROJECT = (
  import.meta.env.VITE_PROMPTER_PROJECT ||
  import.meta.env.VITE_PROJECT_NAME ||
  'default'
).trim() || 'default'

function getProject() {
  // Allow overriding via URL: http://localhost:3050/?project=my_project
  try {
    const urlProject = new URLSearchParams(window.location.search).get('project')
    const p = (urlProject || DEFAULT_PROJECT).trim()
    return p || 'default'
  } catch {
    return DEFAULT_PROJECT
  }
}

function assertArea(area) {
  if (!AREAS.includes(area)) throw new Error(`Invalid area: ${area}`)
}

function assertFile(file) {
  if (!FILES.includes(file)) throw new Error(`Invalid file: ${file}`)
}

export async function fetchInstructionFile(area, file) {
  assertArea(area)
  assertFile(file)

  const project = getProject()
  const res = await fetch(
    `/api/instructions/${encodeURIComponent(project)}/${encodeURIComponent(area)}/${encodeURIComponent(file)}`
  )
  if (!res.ok) throw new Error(`Failed to fetch ${project}/${area}/${file}: ${res.status}`)
  return await res.text()
}

export async function saveInstructionFile(area, file, content) {
  assertArea(area)
  assertFile(file)

  const project = getProject()
  const res = await fetch(
    `/api/instructions/${encodeURIComponent(project)}/${encodeURIComponent(area)}/${encodeURIComponent(file)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'text/plain; charset=utf-8'
      },
      body: content ?? ''
    }
  )

  if (!res.ok) throw new Error(`Failed to save ${project}/${area}/${file}: ${res.status}`)
}

export { AREAS }

const AREAS = ['front-end', 'back-end', 'testing']
const FILES = ['instructions.md', 'completed_instructions.md']

const DEFAULT_PROJECT = (
  import.meta.env.VITE_PROMPTER_PROJECT ||
  import.meta.env.VITE_PROJECT_NAME ||
  'default'
).trim() || 'default'

export function getInitialProject() {
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

export async function fetchProjects() {
  const res = await fetch('/api/projects')
  if (!res.ok) throw new Error(`Failed to fetch projects: ${res.status}`)
  return await res.json()
}

export async function fetchInstructionFile(area, file, project) {
  assertArea(area)
  assertFile(file)

  const p = (project || getInitialProject()).trim() || 'default'
  const res = await fetch(
    `/api/instructions/${encodeURIComponent(p)}/${encodeURIComponent(area)}/${encodeURIComponent(file)}`
  )
  if (!res.ok) throw new Error(`Failed to fetch ${p}/${area}/${file}: ${res.status}`)
  return await res.text()
}

export async function fetchCompletedInstructionFiles(area, project) {
  assertArea(area)
  const p = (project || getInitialProject()).trim() || 'default'

  const res = await fetch(
    `/api/instructions/${encodeURIComponent(p)}/${encodeURIComponent(area)}/completed-files`
  )
  if (!res.ok) throw new Error(`Failed to fetch completed files for ${p}/${area}: ${res.status}`)
  return await res.json()
}

export async function fetchCompletedInstructionFile(area, name, project) {
  assertArea(area)
  const p = (project || getInitialProject()).trim() || 'default'

  const res = await fetch(
    `/api/instructions/${encodeURIComponent(p)}/${encodeURIComponent(area)}/completed-file/${encodeURIComponent(name)}`
  )
  if (!res.ok) throw new Error(`Failed to fetch completed file ${name} for ${p}/${area}: ${res.status}`)
  return await res.text()
}

export async function saveInstructionFile(area, file, content, project) {
  assertArea(area)
  assertFile(file)

  const p = (project || getInitialProject()).trim() || 'default'
  const res = await fetch(
    `/api/instructions/${encodeURIComponent(p)}/${encodeURIComponent(area)}/${encodeURIComponent(file)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'text/plain; charset=utf-8'
      },
      body: content ?? ''
    }
  )

  if (!res.ok) throw new Error(`Failed to save ${p}/${area}/${file}: ${res.status}`)
}

export { AREAS }

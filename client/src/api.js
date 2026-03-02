const AREAS = ['front-end', 'back-end', 'testing']
const FILES = ['instructions.md', 'completed_instructions.md']

function assertArea(area) {
  if (!AREAS.includes(area)) throw new Error(`Invalid area: ${area}`)
}

function assertFile(file) {
  if (!FILES.includes(file)) throw new Error(`Invalid file: ${file}`)
}

export async function fetchInstructionFile(area, file) {
  assertArea(area)
  assertFile(file)

  const res = await fetch(`/api/instructions/${encodeURIComponent(area)}/${encodeURIComponent(file)}`)
  if (!res.ok) throw new Error(`Failed to fetch ${area}/${file}: ${res.status}`)
  return await res.text()
}

export async function saveInstructionFile(area, file, content) {
  assertArea(area)
  assertFile(file)

  const res = await fetch(`/api/instructions/${encodeURIComponent(area)}/${encodeURIComponent(file)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'text/plain; charset=utf-8'
      },
      body: content ?? ''
    }
  )

  if (!res.ok) throw new Error(`Failed to save ${area}/${file}: ${res.status}`)
}

export { AREAS }

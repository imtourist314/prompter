const express = require('express')
const cors = require('cors')
const fs = require('fs')
const path = require('path')

const app = express()

// Accept raw text bodies for PUT.
app.use(express.text({ type: '*/*', limit: '5mb' }))

// CORS for local dev (Vite runs on a different port).
app.use(cors())

// Persistence layout:
//   persistence/<project>/<area>/{instructions.md, completed_instructions.md, completed_instructions.<ts>.md}
//
// Legacy layout (still read as fallback when files are missing in the new layout):
//   persistence/<area>/{instructions.md, completed_instructions.md, completed_instructions.<ts>.md}
const PERSISTENCE_ROOT = path.resolve(__dirname, '../persistence')
const DEFAULT_PROJECT = (process.env.PROMPTER_PROJECT || 'default').trim() || 'default'

const PROJECT_RE = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/
const ALLOWED_AREAS = new Set(['front-end', 'back-end', 'testing'])
const ALLOWED_FILES = new Set(['instructions.md', 'completed_instructions.md'])

const COMPLETED_ALIAS = 'completed_instructions.md'
const COMPLETED_RE = /^completed_instructions\.(\d{8}_\d{6})\.md$/

function ensureProjectAreaDir(project, area) {
  const dir = path.join(PERSISTENCE_ROOT, project, area)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
  return dir
}

function legacyAreaDir(area) {
  return path.join(PERSISTENCE_ROOT, area)
}

function ensureOnDisk(project, area, file) {
  // For "normal" fixed filenames (e.g. instructions.md).
  const dir = ensureProjectAreaDir(project, area)
  const filePath = path.join(dir, file)

  if (fs.existsSync(filePath)) return filePath

  // One-time-ish migration: if the file exists in the legacy location, copy it.
  const legacyPath = path.join(legacyAreaDir(area), file)
  if (fs.existsSync(legacyPath)) {
    fs.copyFileSync(legacyPath, filePath)
    return filePath
  }

  fs.writeFileSync(filePath, '', 'utf8')
  return filePath
}

function formatTimestamp(d = new Date()) {
  const pad = (n) => String(n).padStart(2, '0')
  const yyyy = d.getFullYear()
  const mm = pad(d.getMonth() + 1)
  const dd = pad(d.getDate())
  const hh = pad(d.getHours())
  const mi = pad(d.getMinutes())
  const ss = pad(d.getSeconds())
  return `${yyyy}${mm}${dd}_${hh}${mi}${ss}`
}

function getLatestCompletedInstructionsPath(project, area) {
  const dir = ensureProjectAreaDir(project, area)

  const pickLatest = (d) => {
    if (!fs.existsSync(d)) return null
    const candidates = fs
      .readdirSync(d)
      .filter((name) => COMPLETED_RE.test(name))
      // Filename format sorts naturally by recency.
      .sort()

    if (candidates.length === 0) return null
    return path.join(d, candidates[candidates.length - 1])
  }

  // Prefer the new layout.
  const latest = pickLatest(dir)
  if (latest) return latest

  // Fallback to the legacy layout.
  return pickLatest(legacyAreaDir(area))
}

function getNewCompletedInstructionsPath(project, area, d = new Date()) {
  const dir = ensureProjectAreaDir(project, area)

  // If multiple saves happen within the same second, avoid clobbering by
  // incrementing the timestamp until we find a free filename.
  let dt = d
  for (let i = 0; i < 10; i++) {
    const stamp = formatTimestamp(dt)
    const candidate = path.join(dir, `completed_instructions.${stamp}.md`)
    if (!fs.existsSync(candidate)) return candidate
    dt = new Date(dt.getTime() + 1000)
  }

  // Extremely unlikely fallback.
  const stamp = formatTimestamp(new Date())
  return path.join(dir, `completed_instructions.${stamp}.md`)
}

function validateProject(project) {
  if (!PROJECT_RE.test(project)) {
    const err = new Error(`Invalid project: ${project}`)
    err.status = 400
    throw err
  }
}

function validate(project, area, file) {
  validateProject(project)
  if (!ALLOWED_AREAS.has(area)) {
    const err = new Error(`Invalid area: ${area}`)
    err.status = 400
    throw err
  }
  if (!ALLOWED_FILES.has(file)) {
    const err = new Error(`Invalid file: ${file}`)
    err.status = 400
    throw err
  }
}

function getProjectFromRequest(reqProject) {
  return (reqProject || DEFAULT_PROJECT).trim() || DEFAULT_PROJECT
}

function handleGet(req, res, next, project, area, file) {
  try {
    project = getProjectFromRequest(project)
    validate(project, area, file)

    res.setHeader('Content-Type', 'text/markdown; charset=utf-8')

    // completed_instructions.md is an alias that reads from the most recent
    // completed_instructions.<YYYYMMDD_HHMMSS>.md file.
    if (file === COMPLETED_ALIAS) {
      const latestPath = getLatestCompletedInstructionsPath(project, area)
      if (latestPath) return res.send(fs.readFileSync(latestPath, 'utf8'))

      // Backward-compatible fallback if only the legacy alias file exists.
      const legacyAlias = path.join(legacyAreaDir(area), COMPLETED_ALIAS)
      if (fs.existsSync(legacyAlias)) return res.send(fs.readFileSync(legacyAlias, 'utf8'))

      const aliasPath = ensureOnDisk(project, area, COMPLETED_ALIAS)
      return res.send(fs.readFileSync(aliasPath, 'utf8'))
    }

    const filePath = ensureOnDisk(project, area, file)
    return res.send(fs.readFileSync(filePath, 'utf8'))
  } catch (e) {
    next(e)
  }
}

function handlePut(req, res, next, project, area, file) {
  try {
    project = getProjectFromRequest(project)
    validate(project, area, file)

    const body = req.body ?? ''

    // completed_instructions.md writes a new timestamped snapshot on each save.
    // We also update completed_instructions.md as a convenience pointer for
    // anything that still reads the "static" filename directly from disk.
    if (file === COMPLETED_ALIAS) {
      const tsPath = getNewCompletedInstructionsPath(project, area)
      fs.writeFileSync(tsPath, body, 'utf8')

      const aliasPath = ensureOnDisk(project, area, COMPLETED_ALIAS)
      fs.writeFileSync(aliasPath, body, 'utf8')

      return res.status(204).end()
    }

    const filePath = ensureOnDisk(project, area, file)
    fs.writeFileSync(filePath, body, 'utf8')
    return res.status(204).end()
  } catch (e) {
    next(e)
  }
}

// New endpoint shape (project-aware):
//   GET http://<servername>:<port>/api/instructions/<project>/<front-end|back-end|testing>/instructions.md
app.get('/api/instructions/:project/:area/:file', (req, res, next) => {
  const { project, area, file } = req.params
  return handleGet(req, res, next, project, area, file)
})

app.put('/api/instructions/:project/:area/:file', (req, res, next) => {
  const { project, area, file } = req.params
  return handlePut(req, res, next, project, area, file)
})

// Backward compatible endpoints (no project segment). These route to DEFAULT_PROJECT.
app.get('/api/instructions/:area/:file', (req, res, next) => {
  const { area, file } = req.params
  return handleGet(req, res, next, DEFAULT_PROJECT, area, file)
})

app.put('/api/instructions/:area/:file', (req, res, next) => {
  const { area, file } = req.params
  return handlePut(req, res, next, DEFAULT_PROJECT, area, file)
})

// Serve the built Vue app (if present). In dev, use Vite.
const CLIENT_DIST = path.resolve(__dirname, '../client/dist')
if (fs.existsSync(CLIENT_DIST)) {
  app.use(express.static(CLIENT_DIST))
  app.get('*', (req, res) => {
    res.sendFile(path.join(CLIENT_DIST, 'index.html'))
  })
}

app.use((err, req, res, next) => {
  const status = err.status || 500
  res.status(status).json({ error: err.message || String(err) })
})

const port = process.env.PORT ? Number(process.env.PORT) : 3050
app.listen(port, () => {
  console.log(`Prompter API listening on http://localhost:${port}`)
  console.log(`Persistence root: ${PERSISTENCE_ROOT}`)
  console.log(`Default project: ${DEFAULT_PROJECT}`)
})

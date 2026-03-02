const express = require('express')
const cors = require('cors')
const fs = require('fs')
const path = require('path')

const app = express()

// Accept raw text bodies for PUT.
app.use(express.text({ type: '*/*', limit: '5mb' }))

// CORS for local dev (Vite runs on a different port).
app.use(cors())

const PROJECT_ROOT = path.resolve(__dirname, '../persistence/')
const ALLOWED_AREAS = new Set(['front-end', 'back-end', 'testing'])
const ALLOWED_FILES = new Set(['instructions.md', 'completed_instructions.md'])

const COMPLETED_ALIAS = 'completed_instructions.md'
const COMPLETED_RE = /^completed_instructions\.(\d{8}_\d{6})\.md$/

function ensureAreaDir(area) {
  const dir = path.join(PROJECT_ROOT, area)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
  return dir
}

function ensureOnDisk(area, file) {
  // For "normal" fixed filenames (e.g. instructions.md).
  const dir = ensureAreaDir(area)
  const filePath = path.join(dir, file)

  if (!fs.existsSync(filePath)) fs.writeFileSync(filePath, '', 'utf8')
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

function getLatestCompletedInstructionsPath(area) {
  const dir = ensureAreaDir(area)
  if (!fs.existsSync(dir)) return null

  const candidates = fs
    .readdirSync(dir)
    .filter((name) => COMPLETED_RE.test(name))
    // Filename format sorts naturally by recency.
    .sort()

  if (candidates.length === 0) return null
  return path.join(dir, candidates[candidates.length - 1])
}

function getNewCompletedInstructionsPath(area, d = new Date()) {
  const dir = ensureAreaDir(area)

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

function validate(area, file) {
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

// Required endpoint shape:
//   GET http://<servername>:<port>/api/instructions/<front-end|back-end|testing>/instructions.md
app.get('/api/instructions/:area/:file', (req, res, next) => {
  try {
    const { area, file } = req.params
    validate(area, file)

    res.setHeader('Content-Type', 'text/markdown; charset=utf-8')

    // completed_instructions.md is an alias that reads from the most recent
    // completed_instructions.<YYYYMMDD_HHMMSS>.md file.
    if (file === COMPLETED_ALIAS) {
      const latestPath = getLatestCompletedInstructionsPath(area)
      if (latestPath) return res.send(fs.readFileSync(latestPath, 'utf8'))

      // Backward-compatible fallback if only the legacy file exists.
      const legacyPath = ensureOnDisk(area, COMPLETED_ALIAS)
      return res.send(fs.readFileSync(legacyPath, 'utf8'))
    }

    const filePath = ensureOnDisk(area, file)
    return res.send(fs.readFileSync(filePath, 'utf8'))
  } catch (e) {
    next(e)
  }
})

// Used by the UI submit button to persist.
app.put('/api/instructions/:area/:file', (req, res, next) => {
  try {
    const { area, file } = req.params
    validate(area, file)

    const body = req.body ?? ''

    // completed_instructions.md writes a new timestamped snapshot on each save.
    // We also update completed_instructions.md as a convenience pointer for
    // anything that still reads the "static" filename directly from disk.
    if (file === COMPLETED_ALIAS) {
      const tsPath = getNewCompletedInstructionsPath(area)
      fs.writeFileSync(tsPath, body, 'utf8')

      const aliasPath = ensureOnDisk(area, COMPLETED_ALIAS)
      fs.writeFileSync(aliasPath, body, 'utf8')

      return res.status(204).end()
    }

    const filePath = ensureOnDisk(area, file)
    fs.writeFileSync(filePath, body, 'utf8')
    return res.status(204).end()
  } catch (e) {
    next(e)
  }
})

// Serve the built Vue app (if present). In dev, use Vite.
const CLIENT_DIST = path.join(PROJECT_ROOT, 'client', 'dist')
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
})

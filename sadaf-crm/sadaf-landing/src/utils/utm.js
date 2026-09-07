// UTM capture & persistence
//
// Goal: a person can arrive from any of the targetologists' ads, e.g.
//   https://sadaf.travel/?utm_source=instagram&utm_medium=cpc&utm_campaign=targetolog_1
//   https://sadaf.travel/?utm_source=instagram&utm_campaign=targetolog_2&utm_content=story_ad
// We read those params on the very first load, persist them to localStorage,
// and keep using the SAME stored values for every later page view / form
// submission in that browser — even if the person browses on and the URL
// no longer has the query string. This lets you attribute a lead to the
// exact ad / targetolog that brought the person in.

export const UTM_STORAGE_KEY = 'sadaf_utm_params'

export const UTM_FIELDS = [
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_content',
  'utm_term'
]

/**
 * Reads utm_* query params from the current URL (if present) and stores
 * them in localStorage. If the URL has no UTM params at all, any
 * previously stored values are left untouched, so returning visitors keep
 * their original attribution.
 */
export function captureUtmParams() {
  try {
    const params = new URLSearchParams(window.location.search)
    const found = {}
    let hasAny = false

    UTM_FIELDS.forEach((field) => {
      const value = params.get(field)
      if (value) {
        found[field] = value
        hasAny = true
      }
    })

    if (hasAny) {
      const payload = {
        ...found,
        captured_at: new Date().toISOString(),
        landing_url: window.location.href
      }
      window.localStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(payload))
    }
  } catch (error) {
    // localStorage may be unavailable (private mode, disabled storage, etc.)
    // Fail silently — UTM attribution is a nice-to-have, not critical path.
    console.warn('UTM capture skipped:', error)
  }
}

/**
 * Returns the currently stored UTM params as a plain object containing
 * only utm_source / utm_medium / utm_campaign / utm_content / utm_term
 * (empty string for any field that was never captured).
 */
export function getUtmParams() {
  const empty = UTM_FIELDS.reduce((acc, field) => ({ ...acc, [field]: '' }), {})

  try {
    const raw = window.localStorage.getItem(UTM_STORAGE_KEY)
    if (!raw) return empty

    const stored = JSON.parse(raw)
    return UTM_FIELDS.reduce(
      (acc, field) => ({ ...acc, [field]: stored[field] || '' }),
      {}
    )
  } catch (error) {
    console.warn('Could not read stored UTM params:', error)
    return empty
  }
}

import { getUtmParams } from '../utils/utm'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const LEAD_API_KEY = import.meta.env.VITE_LEAD_API_KEY || ''

/**
 * Submits a lead to the SADAF CRM backend:
 *   POST {API_BASE_URL}/api/integrations/website/lead
 *
 * This is a dedicated public webhook on the CRM (separate from the
 * internal, JWT-protected /api/leads endpoint that logged-in staff use),
 * mirroring the CRM's existing Google Sheets webhook pattern. It is
 * protected by a shared secret sent as the X-Website-Secret header —
 * this MUST match the CRM backend's WEBSITE_WEBHOOK_SECRET env var.
 *
 * Payload:
 *   name, phone, destination, travelDate
 *   + utm_source, utm_medium, utm_campaign, utm_content, utm_term
 *
 * This file only talks to the backend — it does not implement or modify it.
 */
export async function submitLead({ name, phone, destination, travelDate }) {
  if (!API_BASE_URL) {
    throw new Error(
      'VITE_API_BASE_URL aniqlanmagan. .env faylida VITE_API_BASE_URL ni sozlang.'
    )
  }

  const utm = getUtmParams()

  const payload = {
    name,
    phone,
    destination,
    travelDate,
    ...utm
  }

  const response = await fetch(`${API_BASE_URL}/api/integrations/website/lead`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Website-Secret': LEAD_API_KEY
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    let message = `So'rov xatolik bilan yakunlandi (${response.status})`
    try {
      const data = await response.json()
      if (data && data.message) message = data.message
    } catch {
      // response body wasn't JSON — keep the default message
    }
    throw new Error(message)
  }

  try {
    return await response.json()
  } catch {
    return null
  }
}

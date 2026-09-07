/**
 * Google Sheets → SADAF CRM: yangi lead integratsiyasi (Meta Lead Ads jadvali).
 *
 * Bu jadval Facebook/Instagram Lead Ads formidan kelgan leadlarni saqlaydi
 * (ustunlar: id, created_time, ad_id, ad_name, adset_id, adset_name,
 * campaign_id, campaign_name, form_id, form_name, is_organic, platform,
 * ismingiz?, telefon_raqamingiz?, phone_number, lead_status, Comment).
 * Yangi qatorlar bu jadvalga tashqi xizmat (Meta integratsiyasi) tomonidan
 * qo'shiladi — shuning uchun oddiy "On edit" trigger ishonchli ishlamaydi
 * (u faqat qo'lda kiritilgan o'zgarishlarni ushlaydi). Shu sababli bu skript
 * VAQT BO'YICHA (masalan har 5 daqiqada) ishga tushadigan trigger orqali
 * jadvalni skanerlaydi va CRM'ga hali yuborilmagan qatorlarni topib yuboradi.
 *
 * MUHIM: bu skript faqat jadvaldan CRM'ga MA'LUMOT O'QIB YUBORADI — jadvalning
 * o'ziga hech narsa yozmaydi yoki o'chirmaydi. Qaysi qator allaqachon
 * yuborilganini kuzatish uchun jadval ichida emas, skriptning o'z xotirasida
 * (PropertiesService) "oxirgi yuborilgan qator" raqami saqlanadi.
 *
 * O'RNATISH:
 *  1. Google Sheetsda: Extensions → Apps Script.
 *  2. Shu faylning kodini joylashtiring (mavjud kodni almashtiring).
 *  3. CRM_URL va SHEETS_SECRET ni to'ldiring (SHEETS_SECRET backenddagi
 *     .env dagi SHEETS_WEBHOOK_SECRET bilan bir xil bo'lishi shart).
 *  4. Agar jadvalingiz ustunlari boshqacha tartibda bo'lsa — COLUMN_MAP ni
 *     moslang (1-ustundan, A=1, boshlab).
 *  5. Skript muharririda funksiyalar ro'yxatidan `setupTrigger` ni tanlang
 *     va bir marta ishga tushiring (Run tugmasi). Bu avtomatik ravishda
 *     `syncNewLeads` funksiyasini har 5 daqiqada ishga tushiradigan trigger
 *     yaratadi. Birinchi ishga tushirishda Google ruxsat so'raydi — tasdiqlang.
 *  6. Tekshirish uchun `syncNewLeads` ni qo'lda bir marta ishga tushirib,
 *     View → Logs (yoki Executions) orqali natijani ko'rishingiz mumkin.
 */

const CRM_URL = 'https://sizning-domeningiz.uz/api/integrations/sheets/lead';
const SHEETS_SECRET = 'change-me-sheets-secret'; // backend .env dagi SHEETS_WEBHOOK_SECRET bilan bir xil

// Sarlavha qatori tepada bo'lsa DATA_START_ROW = 2 (standart holat).
const DATA_START_ROW = 2;

// Ustun raqamlari (A=1, B=2, ...) — Meta Lead Ads eksporti standart tartibi.
// O'z jadvalingiz boshqacha bo'lsa shu raqamlarni moslang.
const COLUMN_MAP = {
  externalId: 1,    // A — id (Metadagi lead ID, masalan "l:1029005839907742")
  createdTime: 2,   // B — created_time (ISO 8601, masalan "2026-08-06T07:39:23-05:00")
  adName: 4,         // D — ad_name
  campaignName: 8,   // H — campaign_name
  platform: 12,      // L — platform ("ig", "fb", ...)
  name: 13,          // M — ismingiz?
  phoneRaw: 14,      // N — telefon_raqamingiz? (foydalanuvchi qo'lda kiritgan, formatsiz bo'lishi mumkin)
  phoneFormatted: 15,// O — phone_number (Meta normallashtirgan, "p:+998..." ko'rinishida)
  leadStatus: 16,    // P — lead_status
  comment: 17        // Q — Comment
};

/** Har `syncNewLeads` ishga tushganda CRM'ga so'rov yuborilmasligini kafolatlaydi. */
const LOCK_TIMEOUT_MS = 30 * 1000;
const LAST_ROW_KEY = 'sadaf_crm_last_synced_row';

/**
 * Asosiy funksiya — vaqt bo'yicha trigger shuni chaqiradi.
 * Oxirgi yuborilgan qatordan keyingi barcha to'liq qatorlarni CRM'ga jo'natadi.
 */
function syncNewLeads() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(LOCK_TIMEOUT_MS)) {
    Logger.log('Boshqa ishga tushirish davom etyapti, o\'tkazib yuborildi.');
    return;
  }

  try {
    const sheet = SpreadsheetApp.getActiveSheet();
    const lastRow = sheet.getLastRow();
    const props = PropertiesService.getScriptProperties();
    let lastSynced = Number(props.getProperty(LAST_ROW_KEY) || (DATA_START_ROW - 1));

    if (lastRow <= lastSynced) {
      return; // yangi qator yo'q
    }

    let sentCount = 0;
    for (let row = lastSynced + 1; row <= lastRow; row++) {
      const ok = sendRow(sheet, row);
      // Qator bo'sh (hali to'liq yozilmagan) bo'lsa ham "ko'rilgan" deb belgilaymiz —
      // aks holda bo'sh qator doim qayta tekshirilib, keyingi qatorlar tekshirilmay qoladi.
      lastSynced = row;
      if (ok) sentCount++;
    }

    props.setProperty(LAST_ROW_KEY, String(lastSynced));
    Logger.log('Tekshirildi: %s-%s qatorlar, CRM\'ga yuborildi: %s ta.', DATA_START_ROW, lastRow, sentCount);
  } finally {
    lock.releaseLock();
  }
}

/** Bitta qatorni CRM'ga yuboradi. Qator bo'sh/yaroqsiz bo'lsa false qaytaradi. */
function sendRow(sheet, row) {
  const get = (col) => (col ? sheet.getRange(row, col).getValue() : '');

  const name = String(get(COLUMN_MAP.name) || '').trim();
  const phone = normalizePhone(get(COLUMN_MAP.phoneFormatted), get(COLUMN_MAP.phoneRaw));
  if (!name || !phone) return false; // qator to'liq emas — o'tkazib yuboriladi

  const createdTimeRaw = get(COLUMN_MAP.createdTime);
  const payload = {
    name: name,
    phone: phone,
    platform: String(get(COLUMN_MAP.platform) || '').trim(),
    campaign: String(get(COLUMN_MAP.campaignName) || '').trim(),
    ad: String(get(COLUMN_MAP.adName) || '').trim(),
    leadStatus: String(get(COLUMN_MAP.leadStatus) || '').trim(),
    comment: String(get(COLUMN_MAP.comment) || '').trim(),
    createdTime: createdTimeRaw instanceof Date ? createdTimeRaw.toISOString() : String(createdTimeRaw || '').trim(),
    externalId: String(get(COLUMN_MAP.externalId) || '').trim(),
    rowId: row
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'X-Sheets-Secret': SHEETS_SECRET },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(CRM_URL, options);
  const code = response.getResponseCode();
  Logger.log('CRM javobi (%s-qator, %s): %s — %s', row, name, code, response.getContentText());
  return code >= 200 && code < 300;
}

/** "p:+998901234567" → "+998901234567" ko'rinishiga o'giradi; bo'sh bo'lsa qo'l bilan kiritilgan raqamni ishlatadi. */
function normalizePhone(formatted, raw) {
  const f = String(formatted || '').trim();
  if (f) return f.replace(/^p:/i, '').trim();
  return String(raw || '').trim();
}

/**
 * Bir martalik sozlash: `syncNewLeads` uchun har 5 daqiqada ishga tushadigan
 * trigger yaratadi. Skript muharniridan shu funksiyani QO'LDA bir marta
 * ishga tushiring (Run). Qayta ishga tushirsangiz — eski triggerlar
 * tozalanib, faqat bitta trigger qoladi (dublikat bo'lmaydi).
 */
function setupTrigger() {
  ScriptApp.getProjectTriggers()
    .filter((t) => t.getHandlerFunction() === 'syncNewLeads')
    .forEach((t) => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('syncNewLeads')
    .timeBased()
    .everyMinutes(5)
    .create();

  Logger.log('Trigger o\'rnatildi: syncNewLeads har 5 daqiqada ishga tushadi.');
}

/** CRM_URL va SHEETS_SECRET to'g'ri sozlanganini tekshirish uchun — qo'lda ishga tushiring. */
function testConnection() {
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'X-Sheets-Secret': SHEETS_SECRET },
    payload: JSON.stringify({
      name: 'Test Lead',
      phone: '+998900000000',
      platform: 'test',
      comment: 'testConnection() orqali yuborilgan sinov yozuvi'
    }),
    muteHttpExceptions: true
  };
  const response = UrlFetchApp.fetch(CRM_URL, options);
  Logger.log('Test natijasi: %s — %s', response.getResponseCode(), response.getContentText());
}

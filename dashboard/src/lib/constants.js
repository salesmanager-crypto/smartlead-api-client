// Pipedrive company subdomain used to build "Open in Pipedrive" deep links
// (https://{domain}.pipedrive.com/deal/{id}). Matches PIPEDRIVE_COMPANY_DOMAIN in .env.
export const PIPEDRIVE_COMPANY_DOMAIN = "albertscott";

export function pipedriveDealUrl(dealId) {
  return `https://${PIPEDRIVE_COMPANY_DOMAIN}.pipedrive.com/deal/${dealId}`;
}

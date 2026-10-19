/**
 * Formats a capital value (given in Billions) into a human-readable string.
 * - >= 1000 B: Trillions (e.g., $84.10 T)
 * - >= 1 B: Billions (e.g., $1,582.82 B)
 * - < 1 B: Millions (e.g., $14.77 M)
 */
export function formatCapital(billions: number | null | undefined): string {
  if (billions === null || billions === undefined || isNaN(Number(billions))) {
    return "NOT ESTABLISHED";
  }

  const val = Number(billions);

  if (val === 0) {
    return "$0.00 B";
  }

  if (val >= 1000) {
    // Trillions
    return `$${(val / 1000).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} T`;
  } 
  
  if (val >= 1) {
    // Billions
    return `$${val.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} B`;
  } 
  
  // Millions
  return `$${(val * 1000).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} M`;
}

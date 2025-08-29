/**
 * Banker's rounding (round half to even) implementation
 * This matches Python's default rounding behavior for better consistency
 * between frontend and backend.
 * 
 * @param {number} num - The number to round
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {number} The rounded number
 */
export function bankerRound(num, decimals = 1) {
  const factor = Math.pow(10, decimals);
  const shifted = num * factor;
  const floor = Math.floor(shifted);
  const decimal = shifted - floor;
  
  // Check if decimal part is exactly 0.5 (considering floating point precision)
  if (Math.abs(decimal - 0.5) < Number.EPSILON) {
    // Round to nearest even number
    return floor % 2 === 0 ? floor / factor : (floor + 1) / factor;
  } else {
    // Standard rounding for other cases
    return Math.round(shifted) / factor;
  }
}

/**
 * Format movie rating using banker's rounding
 * @param {number} rating - The raw rating value
 * @returns {string} Formatted rating string with 1 decimal place
 */
export function formatMovieRating(rating) {
  if (!rating && rating !== 0) return '0.0';
  return bankerRound(rating, 1).toFixed(1);
}

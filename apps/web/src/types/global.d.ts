declare module "date-fns" {
  export function format(date: Date | number, formatStr: string, options?: object): string;
  export function parse(dateStr: string, formatStr: string, reference: Date, options?: object): Date;
  export function addDays(date: Date, amount: number): Date;
  export function startOfDay(date: Date): Date;
  export function endOfDay(date: Date): Date;
  export function isAfter(date: Date, dateToCompare: Date): boolean;
  export function isBefore(date: Date, dateToCompare: Date): boolean;
  export function differenceInDays(dateLeft: Date, dateRight: Date): number;
}

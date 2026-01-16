# FE-13: TRADE HISTORY TABLE SPECIFICATION
**Component ID:** FE-13  
**Layer:** Component (Data Display)  
**Lib:** TanStack Table (React Table v8) + Headless UI

---

## 1. 🖼️ Visual Structure
A high-density data table with glassmorphism headers and row hover effects.

### Columns Layout
| Status | Pair | Side | Entry | Exit | P&L | Duration | Actions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `[OPEN]` | `BTC/USDT` | `LONG` | `$42,100` | `-` | `+$12.50` | `2h 10m` | `[Close]` |

- **Header:** `bg-dark-800/50` text-gray-400 uppercase text-xs tracking-wider.
- **Row:** `border-b border-dark-700` hover `bg-white/5`.
- **Badges:**
  - **Status:** Pill (Open=Blue, Closed=Gray, Error=Red).
  - **Side:** Text Color (Long=Green, Short=Red).
- **P&L:** Dynamic color (Green if > 0, Red if < 0).

## 2. 🧩 Functionality

### 2.1 Filters & Sorting
- **Global Filter:** Search input "Search Symbol..."
- **Column Sorting:** Click header to toggle ASC/DESC.
- **Pagination:** "Page 1 of 5 | Go to page: [ ]".

### 2.2 Row Actions
- **Close Position:** Only visible if Status = OPEN. Triggers FE-18 Modal.
- **View Details:** Opens sidebar or modal with trade logs.

## 3. 🧬 React Implementation

```tsx
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table';

export default function TradeTable({ data }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="rounded-2xl border border-dark-700 overflow-hidden bg-dark-900">
      
      {/* Visual Header */}
      <div className="p-4 border-b border-dark-700 flex justify-between items-center bg-dark-800/30">
        <h3 className="font-semibold text-white">Recent Activity</h3>
        <input 
          placeholder="Filter trades..." 
          className="bg-dark-950 border border-dark-700 rounded-lg px-3 py-1.5 text-sm text-white"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-dark-800/50">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th key={header.id} className="px-6 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-dark-700/50">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="hover:bg-primary-500/5 transition-colors">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-6 py-4 text-sm text-gray-300">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Pagination Footer */}
      <div className="p-4 border-t border-dark-700 flex justify-center text-sm text-gray-500">
        Pagination Controls
      </div>
    </div>
  );
}
```

## 4. 🎨 Styling Notes
- **Empty State:** If no data, show a centered illustration "No trades found".
- **Responsive:** On mobile, hide less important columns (Entry, Exit) or switch to Card view.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.


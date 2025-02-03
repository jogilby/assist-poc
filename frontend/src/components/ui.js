export function Button({ children, onClick, disabled, className }) {
    return (
      <button
        onClick={onClick}
        disabled={disabled}
        className={`px-4 py-2 bg-blue-500 text-white rounded ${className}`}
      >
        {children}
      </button>
    );
  }
  
  export function Input({ type, placeholder, value, onChange }) {
    return (
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="border p-2 rounded w-full"
      />
    );
  }
  
  export function Select({ value, onChange, children }) {
    return (
      <select value={value} onChange={onChange} className="border p-2 rounded w-full">
        {children}
      </select>
    );
  }
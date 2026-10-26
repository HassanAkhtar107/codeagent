import React from "react";

const InputSelect = ({ label, placeholder, data, value, handleChange, name }) => {

  return (
    <div className="mt-3">
      <label className="text-[rgb(38,42,65)] text-[13px] font-[550] block">
        {label}
      </label>
      <select
        value={value}
        name={name}
        onChange={(e) => handleChange(name, e.target.value)}
        id="countries"
        class="border mt-2 focus:outline-none border-gray-300 text-gray-900 text-sm rounded-[5px] block w-full px-1 py-3"
      >
        <option value="" disabled hidden>{placeholder}</option>
        {
          data && data.map((item, i) => {
            return (
              <option key={item.id} value={item.value}>{item.label}</option>
            )
          })
        }
      </select>
    </div>
  );
};

export default InputSelect;

import React from 'react'

const Input = ({ label, placeholder, name, handleChange, type = "text", value, required, error }) => {
  return (
    <div className='mt-3'>
      <label className='text-[rgb(38,42,65)] text-[13px] font-[550] block' htmlFor="">{label}{required && <span className='text-red-500 text-[18px]'>*</span>}</label>
      <input onChange={(e) => handleChange(name, e.target.value)} value={value} type={type} placeholder={placeholder} name={name} className='w-full p-2 mt-[6px] dark:text-[rgb(38,42,65)] rounded-[5px] focus:outline-none border border-[rgb(194,190,190)] placeholder:text-[14px]' />
      {error && <p className="text-red-500 text-[12px] mt-1">{error}</p>}
    </div>
  )
}

export default Input
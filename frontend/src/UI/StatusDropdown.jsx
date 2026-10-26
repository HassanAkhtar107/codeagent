"use client";
import React, { useState } from "react";
import { FaSortNumericUpAlt } from "react-icons/fa";
import { IoIosArrowDown, IoIosArrowUp } from "react-icons/io";

const StatusDropdown = ({ handleStatus }) => {
  const [check, setCheck] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState("");

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setCheck(true)}
      onMouseLeave={() => setCheck(false)}
    >
      {/* Trigger button */}
      <div className="px-1 w-[120px] rounded-[3px] dark:text-gray-500 cursor-pointer flex items-center justify-between bg-[rgb(226,229,232)]">
        <FaSortNumericUpAlt />
        <h1>Status</h1>
        {check ? <IoIosArrowUp /> : <IoIosArrowDown />}
      </div>

      {/* Dropdown */}
      <div
        className={`w-[120px] bg-white shadow absolute top-6 left-0 px-3 py-2 rounded-[5px] z-10 transition-opacity duration-150 ${check ? "opacity-100 visible" : "opacity-0 invisible"
          }`}
      >
        {/* Active */}
        <label className="flex items-center justify-between cursor-pointer">
          <h1 className="text-[rgb(129,130,140)]">Active</h1>
          <input
            type="radio"
            name="status"
            value="active"
            checked={selectedStatus === "active"}
            onChange={(e) => {
              setSelectedStatus(e.target.value);
              handleStatus(e.target.value);
            }}
          />
        </label>

        {/* Deactive */}
        <label className="flex items-center justify-between mt-2 cursor-pointer">
          <h1 className="text-[rgb(129,130,140)]">Deactive</h1>
          <input
            type="radio"
            name="status"
            value="deactive"
            checked={selectedStatus === "deactive"}
            onChange={(e) => {
              setSelectedStatus(e.target.value);
              handleStatus(e.target.value);
            }}
          />
        </label>
      </div>
    </div>
  );
};

export default StatusDropdown;

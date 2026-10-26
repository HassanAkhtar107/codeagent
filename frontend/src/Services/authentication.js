import {
  login_url,
} from "./urls";

export const loginApi = async (object) => {
  try {
    const res = await fetch(login_url, {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify(object),
    });

    const data = await res.json();

    if (!res.ok) {
      return {
        success: false,
        message: data.non_field_errors
          ? data.non_field_errors[0]
          : "Invalid credentials",
      };
    }

    localStorage.setItem("token", data.token);
    localStorage.setItem("type", data.user.user_type)

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || "Something went wrong",
    };
  }
};

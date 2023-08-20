import { createSlice } from "@reduxjs/toolkit";

export const userSlice = createSlice({
  name: "user",
  initialState: {
    userInfo: {},
    auth: 0,
  },
  reducers: {
    setUserLogin: (state, action) => {
      state.userInfo = action.payload;
    },
    setUserLogout: (state, _) => {
      state.userInfo = {};
      state.auth = 0;
    },
    setUserAuth: (state, action) => {
      state.auth = action.payload;
    },
  },
});

export const { setUserLogin, setUserLogout, setUserAuth } = userSlice.actions;

export const selectUserInfo = state => state.user.userInfo;
export const selectUserAuth = state => state.user.auth;

export default userSlice.reducer;

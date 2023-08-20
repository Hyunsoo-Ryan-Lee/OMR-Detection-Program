import ReactDOM from "react-dom/client";
import { configureStore } from "@reduxjs/toolkit";
import { Provider } from "react-redux";
import { combineReducers } from "redux";
import { persistStore, persistReducer } from "redux-persist";
import { PersistGate } from "redux-persist/integration/react";

import storage from "redux-persist/lib/storage";
import thunk from "redux-thunk";

import userReducer from "redux/User";
import scanReducer from "redux/Scan";
import App from "./App";

import "./index.css";

const persistConfig = {
  key: "root",
  storage,
};

const reducers = combineReducers({
  user: userReducer,
  scan: scanReducer,
});

const persistedReducer = persistReducer(persistConfig, reducers);

const store = configureStore({
  reducer: persistedReducer,
  devTools: process.env.NODE_ENV !== "production",
  middleware: [thunk],
});

let persistor = persistStore(store);

ReactDOM.createRoot(document.getElementById("root")).render(
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <App />
    </PersistGate>
  </Provider>
);

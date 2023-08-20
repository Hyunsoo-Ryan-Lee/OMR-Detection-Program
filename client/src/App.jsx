import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "components/Header";
import LoginPage from "views/LoginPage";

import MainPage from "views/MainPage";

import AdminPage from "views/AdminPage";
import UserPageRouter from "views/UserPage/UserPageRouter";

import ScanPageRouter from "views/ScanPage/ScanPageRouter";

import NotFoundPage from "views/NotFoundPage";

import PrivateRoute from "views/PrivateRoute";

const App = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <PrivateRoute isAdmin={true}>
                <AdminPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/user/*"
            element={
              <PrivateRoute>
                <UserPageRouter />
              </PrivateRoute>
            }
          />

          <Route
            path="/index"
            element={
              <PrivateRoute>
                <MainPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/scan/*"
            element={
              <PrivateRoute>
                <ScanPageRouter />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default App;

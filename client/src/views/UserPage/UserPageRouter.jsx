import { Routes, Route } from "react-router-dom";

import UserInfoPage from "views/UserPage/UserInfoPage";
import UserRegisterPage from "views/UserPage/UserRegisterPage";

import PrivateRoute from "views/PrivateRoute";

const UserPageRouter = () => {
  return (
    <>
      <Routes>
        <Route path="/:user_object_id" element={<UserInfoPage />} />
        <Route
          path="/register"
          element={
            <PrivateRoute isAdmin={true}>
              <UserRegisterPage />
            </PrivateRoute>
          }
        />
      </Routes>
    </>
  );
};

export default UserPageRouter;

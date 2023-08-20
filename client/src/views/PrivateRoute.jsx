import { Navigate } from "react-router-dom";

import { useTools } from "libs/utils";
import { selectUserAuth } from "redux/User";

function PrivateRoute({ children, isAdmin }) {
  const { useSelector } = useTools;
  const userAuth = useSelector(selectUserAuth);

  if (!userAuth) {
    alert("로그인후 이용해 주세요");
    return <Navigate to="/" replace />;
  } else {
    if (isAdmin && userAuth !== 1) {
      alert("관리자만 이용가능합니다");
      return <Navigate to="/index" replace />;
    }
  }
  return children;
}

export default PrivateRoute;

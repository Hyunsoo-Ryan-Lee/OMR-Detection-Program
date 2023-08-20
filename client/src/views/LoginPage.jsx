import { setUserLogin, setUserAuth, selectUserAuth } from "redux/User";
import { resetScanType } from "redux/Scan";

import Button from "components/Button";
import Input from "components/Input";

import { useTools } from "libs/utils";

import logo_img from "static/images/g-logo_icon.png";

const LoginPage = () => {
  const { useEffect, useState, useNavigate, useDispatch, useSelector, api } =
    useTools;
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userAuth = useSelector(selectUserAuth);

  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordWarning, setPasswordWarning] = useState("");

  const onChangeUserName = ({ target: { value } }) => setUserName(value);
  const onChangePassword = ({ target: { value } }) => setPassword(value);

  const handleSubmit = e => {
    e.preventDefault();
    if (userName && password) {
      api
        .post("/api/login", {
          user_id: userName,
          user_pwd: password,
        })
        .then(res => res.data)
        .then(res => {
          const { status, data } = res;
          if (!status) {
            alert("로그인에 실패했습니다. 다시 시도해 주세요");
          } else {
            const { _id, user_id, user_name, user_level, authToken } = data;
            const userInfo = {
              userObjectId: _id.$oid,
              userId: user_id,
              name: user_name,
              auth: user_level,
              token: authToken,
            };
            dispatch(setUserLogin(userInfo));
            dispatch(setUserAuth(user_level));
            dispatch(resetScanType());
            navigate("/index");
          }
        });
    } else {
      setPasswordWarning("비밀번호가 일치하지 않습니다 (초기: admin/12345)");
    }
  };

  useEffect(() => {
    if (userAuth > 0) {
      alert("이미 로그인이 되어 있습니다.");
      navigate("/index");
    }
  }, []);

  return (
    <div className="flex flex-col items-center px-4 h-screen justify-center pb-96">
      <div>
        <img className="mt-32 h-32" src={logo_img} />
      </div>
      <div className="mt-8">
        <form className="flex flex-col mt-8" onSubmit={handleSubmit}>
          <div className="mt-1">
            <div className="flex flex-cols items-center justify-center">
              <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                아이디
              </label>
              <Input
                type="user"
                large={false}
                required
                onChange={onChangeUserName}
              />
            </div>
            <div className="flex flex-cols items-center justify-center mt-4">
              <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                비밀번호
              </label>
              <Input
                type="password"
                large={false}
                required
                onChange={onChangePassword}
              />
            </div>
          </div>
          <div className="mt-4 w-full">
            <p className="text-sm text-red-500 h-6">{passwordWarning}</p>
            <Button type="submit" text="로그인" main={true} />
          </div>
        </form>
      </div>
    </div>
  );
};
export default LoginPage;

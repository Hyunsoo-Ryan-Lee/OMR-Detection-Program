import { useTools } from "libs/utils";

import Button from "components/Button";
import Input from "components/Input";
import { selectUserInfo, selectUserAuth } from "redux/User";

const UserInfoPage = () => {
  const { useState, useNavigate, useEffect, useParams, useSelector, api } =
    useTools;
  const navigate = useNavigate();

  const { user_object_id: userObjectId } = useParams();
  const userInfo = useSelector(selectUserInfo);
  const userAuth = useSelector(selectUserAuth);

  const [userId, setUserId] = useState("");
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [rePassword, setRePassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  const handleSubmit = e => {
    e.preventDefault();
    if (password !== rePassword) {
      alert("비밀번호가 다릅니다. 다시 입력해 주세요.");
    } else {
      const data = {
        user_name: userName,
        user_pwd: password,
        user_level: isAdmin ? 1 : 2,
        authToken: userInfo.token,
      };

      api
        .put(`/api/users/${userObjectId}`, data)
        .then(res => res.data)
        .then(res => {
          if (res.status) {
            alert("수정되었습니다");
          }
        });
    }
  };

  useEffect(() => {
    api
      .get(`/api/users/${userObjectId}`)
      .then(res => res.data)
      .then(res => {
        const userData = res.data;
        setUserId(userData.user_id);
        setUserName(userData.user_name);
        setIsAdmin(userData.user_level === 1 ? true : false);
      });
  }, []);

  return (
    <div className="mt-6 mx-12">
      <div className="mt-24 flex flex-col items-center gap-4">
        <div className="w-1/3">
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
                  value={userId}
                  onChange={e => setUserId(e.target.value)}
                  disabled={userAuth === 1 ? true : false}
                />
              </div>
              <div className="flex flex-cols items-center justify-center mt-4">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  사용자 이름
                </label>
                <Input
                  type="user"
                  large={false}
                  required
                  value={userName}
                  onChange={e => setUserName(e.target.value)}
                />
              </div>
              <div className="flex flex-cols items-center justify-center mt-4">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  비밀번호 재설정
                </label>
                <Input
                  type="password"
                  large={false}
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                />
              </div>
              <div className="flex flex-cols items-center justify-center mt-4">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  비밀번호 재입력
                </label>
                <Input
                  type="password"
                  large={false}
                  required
                  value={rePassword}
                  onChange={e => setRePassword(e.target.value)}
                />
              </div>
              <div className="flex flex-cols items-center justify-start mt-4">
                <label className="text-sm font-medium text-gray-700 items-start px-4 w-40">
                  관리자 여부
                </label>
                <div className="w-full">
                  <input
                    type="checkbox"
                    className="text-teal-600 rounded border-gray-300 focus:ring-teal-400 dark:focus:ring-teal-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                    checked={isAdmin}
                    onChange={e => {
                      setIsAdmin(e.target.checked);
                    }}
                  />
                </div>
              </div>
            </div>
            <div className="flex flex-col mt-6">
              <Button type="submit" text="수정하기" main={true} />
              {userAuth === 1 ? (
                <Button
                  text="관리자 화면으로"
                  onClick={() => {
                    navigate("/admin");
                  }}
                />
              ) : (
                <></>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserInfoPage;

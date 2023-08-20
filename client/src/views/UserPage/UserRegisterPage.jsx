import { useTools } from "libs/utils";

import Button from "components/Button";
import Input from "components/Input";
import { selectUserAuth } from "redux/User";

const UserPage = () => {
  const { useState, useNavigate, useSelector, api } = useTools;

  const navigate = useNavigate();
  const userAuth = useSelector(selectUserAuth);

  const [userId, setUserId] = useState("");
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [rePassword, setRePassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(userAuth === 1 ? true : false);

  const handleSubmit = e => {
    e.preventDefault();

    const userData = {
      user_id: userId,
      user_name: userName,
      user_pwd: password,
      user_level: isAdmin ? 1 : 2,
    };

    if (password !== rePassword) {
      alert("비밀번호 재입력이 다릅니다. 다시 입력해 주세요");
    } else {
      api
        .post("/api/users", userData)
        .then(res => res.data)
        .then(_ => {
          alert("성공적으로 등록되었습니다.");
          navigate("/admin");
        });
    }
  };

  return (
    <div className="mt-6 mx-12">
      <div className="mt-24 flex flex-col items-center gap-4">
        <div>등록 페이지</div>
        <div className="w-1/3">
          <form className="flex flex-col mt-8" onSubmit={handleSubmit}>
            <div className="mt-1">
              <div className="flex flex-cols items-center justify-center">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  아이디
                </label>
                <Input
                  type="userId"
                  large={false}
                  required
                  value={userId}
                  onChange={e => setUserId(e.target.value)}
                />
              </div>
              <div className="flex flex-cols items-center justify-center mt-4">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  사용자 이름
                </label>
                <Input
                  type="userName"
                  large={false}
                  required
                  value={userName}
                  onChange={e => setUserName(e.target.value)}
                />
              </div>
              <div className="flex flex-cols items-center justify-center mt-4">
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-40">
                  비밀번호 입력
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
                <label className="text-sm font-medium text-gray-700 items-end px-4 w-36">
                  관리자 여부
                </label>
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
            <div className="mt-6">
              <Button type="submit" text="등록하기" main={true} />
            </div>
          </form>
        </div>
        {userAuth === 1 ? (
          <div className="mt-4 w-1/3">
            <Button
              text="관리자 화면으로"
              onClick={() => {
                navigate("/admin");
              }}
            />
          </div>
        ) : (
          <></>
        )}
      </div>
    </div>
  );
};

export default UserPage;

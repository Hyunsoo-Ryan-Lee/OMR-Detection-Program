import { selectUserInfo, selectUserAuth, setUserLogout } from "redux/User";

import { useTools } from "libs/utils";

import Button from "components/Button";
import HomeIcon from "static/icons/HomeIcon";
import UserIcon from "static/icons/UserIcon";
import logo_img from "static/images/g-logo.png";

const Header = () => {
  const { useNavigate, useDispatch, useSelector } = useTools;
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userInfo = useSelector(selectUserInfo);
  const auth = useSelector(selectUserAuth);

  return (
    <div className="bg-teal-400 text-white py-2">
      <div className="grid grid-cols-3 items-center justify-center px-10">
        <div
          className="w-10 cursor-pointer"
          onClick={() => {
            navigate("/index");
          }}
        >
          <HomeIcon />
        </div>
        <div className=" flex flex-col items-center">
          <img
            className="h-14 cursor-pointer"
            src={logo_img}
            onClick={() => {
              navigate(auth ? "/index" : "/");
            }}
          />
        </div>
        <div className="flex flex-row items-center justify-end gap-4">
          {auth > 0 ? (
            <>
              <div>
                <div className="font-bold">{userInfo.name}님</div> 반갑습니다
              </div>
              <div
                className="flex flex-col items-center justify-center cursor-pointer"
                onClick={() => {
                  navigate(`/user/${userInfo.userObjectId}`);
                }}
              >
                <UserIcon />
                <p className="text-[10px]">my page</p>
              </div>
              <div>
                <Button
                  text="로그아웃"
                  onClick={() => {
                    dispatch(setUserLogout());
                    navigate("/");
                  }}
                />
              </div>
            </>
          ) : (
            <div>
              <Button
                text="로그인"
                onClick={() => {
                  navigate("/");
                }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default Header;

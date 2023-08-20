import Button from "components/Button";
import { useTools } from "libs/utils";

import { selectUserAuth } from "redux/User";

const MainPage = () => {
  const { useNavigate, useSelector } = useTools;
  const navigate = useNavigate();
  const userAuth = useSelector(selectUserAuth);

  return (
    <div className="mt-32 mx-12">
      <div className="flex justify-center px-2">
        <div className="flex flex-col items-center m-32 gap-2 w-2/5 ">
          <Button
            className="font-bold bg-teal-100 "
            text="처리작업"
            disabled={true}
          />
          <div className="flex flex-row w-full h-24">
            <Button
              className=""
              text="답안지 스캔 판독"
              main={true}
              onClick={() => {
                navigate("/scan");
              }}
            />
          </div>

          {userAuth === 1 ? (
            <div className="flex flex-row w-full h-24">
              <Button
                className=""
                text="유저 관리 (관리자 화면)"
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
    </div>
  );
};
export default MainPage;

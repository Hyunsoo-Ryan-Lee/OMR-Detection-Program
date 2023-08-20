import { useTools } from "libs/utils";

import Button from "components/Button";

import { selectUserInfo } from "redux/User";

import Pagination from "views/Pagination";

const AdminPage = () => {
  const { useState, useNavigate, useSelector, useEffect, api } = useTools;
  const navigate = useNavigate();
  const userInfo = useSelector(selectUserInfo);

  const colName = ["No", "아이디", "이름", "구분", "관리"];
  const [userInfoArray, setUserInfoArray] = useState([]);

  const onClickDeleteUser = userObjectId => {
    if (window.confirm("삭제하시겠습니까?")) {
      const data = { authToken: userInfo.token };
      api
        .delete(`/api/users/${userObjectId}`, { data })
        .then(res => res.data)
        .then(res => {
          if (res.status) {
            alert("삭제되었습니다");
            window.location.reload();
          }
        });
    }
  };

  const [totalData, setTotal] = useState([]);
  const [limit, setLimit] = useState(10);
  const [page, setPage] = useState(1);
  const offset = (page - 1) * limit;

  const tableColumn = column => {
    return column.map((elem, idx) => {
      return (
        <th
          className="border border-slate-300 bg-slate-200 w-32 p-2"
          key={`${elem}_${idx}`}
        >
          {elem}
        </th>
      );
    });
  };

  const tableComponent = data => {
    return (
      <tbody>
        {data.slice(offset, offset + limit).map(row => {
          const [userObjectId, ..._row] = row;
          return (
            <tr className="hover:bg-slate-100" key={`${userObjectId}`}>
              {_row.map((col, idx) => {
                return (
                  <td
                    className="border border-y-1 border-slate-300"
                    key={`${userObjectId}_${idx}_${col}`}
                  >
                    {idx === 1 && col === 0 ? "없음" : col}
                  </td>
                );
              })}

              <td className="border border-x-1 border-slate-300">
                <div className="flex justify-center">
                  <div
                    className="border border-teal-400  w-24 p-1.5 m-2 text-teal-400 text-sm rounded-md cursor-pointer"
                    onClick={() => {
                      navigate(`/user/${userObjectId}`);
                    }}
                  >
                    수정
                  </div>

                  <div
                    className="border-2 border-teal-400 bg-teal-400 w-24 p-1.5 m-2 text-white text-sm rounded-md cursor-pointer"
                    onClick={() => {
                      onClickDeleteUser(userObjectId);
                    }}
                  >
                    삭제
                  </div>
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    );
  };

  useEffect(() => {
    api
      .get("/api/users")
      .then(res => res.data)
      .then(res => {
        const resData = res.data;
        setTotal(resData);
        let userData = [];
        resData.forEach((elem, idx) => {
          const { _id, user_id, user_name, user_level } = elem;
          const eachUser = [
            _id.$oid,
            idx + 1,
            user_id,
            user_name,
            user_level === 1 ? "관리자" : "사용자",
          ];
          userData.push(eachUser);
        });
        setUserInfoArray(userData);
      });
  }, []);

  return (
    <div className="mt-6 mx-12">
      <div className="flex flex-col gap-4">
        <div className="overflow-x-auto border rounded-md">
          <table className="w-full text-center">
            <thead>
              <tr>{tableColumn(colName)}</tr>
            </thead>
            {tableComponent(userInfoArray)}
          </table>
        </div>

        <div className="flex flex-col gap-4">
          <Pagination
            total={totalData.length}
            limit={limit}
            page={page}
            setPage={setPage}
          />
        </div>

        <div className="flex flex-row justify-end">
          <Button
            className="w-64"
            text="등록"
            onClick={() => {
              navigate("/user/register");
            }}
            main={true}
          />
        </div>
      </div>
    </div>
  );
};

export default AdminPage;

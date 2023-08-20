import { selectScanType } from "redux/Scan";

import { cls, useTools } from "libs/utils";

import { setErrorIdx } from "redux/Scan";

const ScanTableComponent = ({ data, method }) => {
  const { useNavigate, useDispatch, useSelector } = useTools;

  const navigate = useNavigate();
  const dispatch = useDispatch();
  const scanType = useSelector(selectScanType);

  const chkMetaTypeArr = ["유아", "초등", "중등", "고등"];
  const chkTypeArr = [
    "개인번호",
    "학년/반/번호",
    "학생 학년/반/번호",
    "자녀의 학년/반/번호",
    "임시배정번호",
  ];

  let tableContents = [];
  let columns = [];
  let dupliCheck = new Set();

  for (const [index, element] of data.entries()) {
    const { resultId, valueList, specialBack } = element;
    if (!dupliCheck.has(resultId)) {
      dupliCheck.add(resultId);
    } else {
      continue;
    }

    let valueArr = [resultId];
    let colNameArr = ["No"];

    for (let [type, value] of valueList) {
      colNameArr.push(type);
      // if (
      //   chkMetaTypeArr.includes(scanType.value) &&
      //   chkTypeArr.includes(type)
      // ) {
      //   value = value.replaceAll(" ", "*");
      // }
      valueArr.push(value);
    }
    if (specialBack && specialBack.length > 0) {
      colNameArr.push("Ⅲ");
      valueArr.push(specialBack);
    }
    if (columns.length === 0) {
      columns = colNameArr;
    }
    tableContents.push(valueArr);
  }

  const onClickErrorIdx = (index, _id) => {
    if (method !== "normal") {
      dispatch(setErrorIdx(index));
      navigate(`/scan/result/${_id}`);
    }
  };

  const tableColumn = column => {
    return column.map((elem, idx) => {
      return (
        <th
          className="border border-slate-300 bg-slate-200"
          key={`${elem}_${idx}`}
        >
          <p className="p-1 w-full truncate">{elem}</p>
        </th>
      );
    });
  };

  const tableComponent = data => {
    return data.map((row, index) => {
      const [resultId, ..._] = row;
      return (
        <tr
          className={cls(
            "hover:bg-slate-100",
            method !== "normal" ? "hover:cursor-pointer" : ""
          )}
          onClick={() => {
            onClickErrorIdx(index, resultId);
          }}
          key={`${index}_${resultId}`}
        >
          {row.map((col, idx) => {
            return (
              <td
                className="border border-y-1 border-slate-300 w-full"
                key={`${resultId}_${idx}_${col}`}
              >
                <div className="p-1 truncate">
                  {idx === 0
                    ? `...${col.slice(col.length - 6, col.length)}`
                    : col}
                </div>
              </td>
            );
          })}
        </tr>
      );
    });
  };

  return (
    <table className="table-auto w-screen text-center text-sm">
      <thead>
        <tr>{tableColumn(columns)}</tr>
      </thead>
      <tbody>{tableComponent(tableContents)}</tbody>
    </table>
  );
};

export default ScanTableComponent;

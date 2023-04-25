// @ts-nocheck
import generatePicker from "antd/es/date-picker/generatePicker";
import { DateTime } from "luxon";
import luxonGenerateConfig from "rc-picker/lib/generate/luxon";
import { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

const MyDatePicker = generatePicker(luxonGenerateConfig);
const { RangePicker } = MyDatePicker;

function App() {
	const [value, setValue] = useState([DateTime.now(), DateTime.now()]);
	useEffect(() => Streamlit.setFrameHeight());

	return (
		<RangePicker
			// onChange={(value) => console.log(value)}
			format={"dd/MM/yyyy HH:mm:ss"}
			showTime={true}
			open={true}
			value={value}
			onChange={([start, end]) => setValue([start, end])}
			onOk={() => Streamlit.setComponentValue(value.map((v) => v.toISO()))}
		/>
	);
}

export default withStreamlitConnection(App);

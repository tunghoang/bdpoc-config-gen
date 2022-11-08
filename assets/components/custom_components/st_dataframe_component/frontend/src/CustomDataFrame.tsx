import { useEffect, useState } from "react";
import {
	ComponentProps,
	Streamlit,
	withStreamlitConnection,
} from "streamlit-component-lib";
import { Table, TextInput, MantineProvider, Button } from "@mantine/core";
import { CSVLink } from "react-csv";
import React from "react";

/**
 * We can use a Typescript interface to destructure the arguments from Python
 * and validate the types of the input
 */
interface Data {
	_field: string;
	Min: number;
	Max: number;
	Group: string;
	Description: string;
	Unit: string;
	LLL: number;
	LL: number;
	L: number;
	H: number;
	HH: number;
	HHH: number;
	Flag: number;
	Evaluation: string;
	comment?: string;
}

/**
 * No more props manipulation in the code.
 * We store props in state and pass value directly to underlying Slider
 * and then back to Streamlit.
 */
declare type CustomComponentProps = Partial<ComponentProps>;

const CustomDataFrame = (props: CustomComponentProps) => {
	// Destructure using Typescript interface
	// This ensures typing validation for received props from Python
	// console.log(props.args);
	let data: Data[] = [];
	if (Object.keys(props).length > 0) {
		data = props?.args?.data;
	}

	useEffect(() => Streamlit.setFrameHeight());
	const [dataWithComments, setDataWithComments] = useState<Data[]>(data);
	const handleSetDataWithComments = (value: string, index: number) => {
		setDataWithComments((prev) => [
			...prev.slice(0, index),
			Object.assign({}, prev[index], { comment: value }),
			...prev.slice(index + 1),
		]);
	};

	const rows = data.map((item, index) => (
		<tr key={index}>
			{Object.values(item).map((value, _index) => (
				<td key={_index}>{value}</td>
			))}
			<td>
				<TextInput
					placeholder="Comment?"
					value={dataWithComments[index]["comment"]}
					onChange={(e) =>
						handleSetDataWithComments(e.target.value, index)
					}></TextInput>
			</td>
		</tr>
	));

	return (
		<MantineProvider
			theme={{
				colorScheme: "light",
				colors: {
					light: ["E53E3E", "FFFFFF"],
				},
			}}>
			<CSVLink data={dataWithComments} target="_blank" filename="data.csv">
				<Button variant="outline">Download</Button>
			</CSVLink>
			<Table highlightOnHover withBorder withColumnBorders>
				<thead>
					<tr>
						<th>Field</th>
						<th>Min</th>
						<th>Max</th>
						<th>Group</th>
						<th>Description</th>
						<th>Unit</th>
						<th>LLL</th>
						<th>LL</th>
						<th>L</th>
						<th>H</th>
						<th>HH</th>
						<th>HHH</th>
						<th>Flag</th>
						<th>Evaluation</th>
						<th>Comment</th>
					</tr>
				</thead>
				<tbody>{rows}</tbody>
			</Table>
		</MantineProvider>
	);
};

export default withStreamlitConnection(CustomDataFrame);

import { useEffect, useState } from "react";
import {
	Streamlit,
	withStreamlitConnection,
	ArrowTable,
} from "streamlit-component-lib";
import { Checkbox, Row, Col, Typography } from "antd";
import { Table } from "apache-arrow";
import "./App.css";

const FilterOptions = ({ onChange, options, span }) => {
	return (
		<Checkbox.Group onChange={onChange}>
			<Row gutter={[16, 16]}>
				{options.map((option, index) => {
					return (
						<Col span={span} key={index}>
							<Checkbox value={option}>{option}</Checkbox>
						</Col>
					);
				})}
			</Row>
		</Checkbox.Group>
	);
};

const filterTable = (table, condition) => {
	const filteredData = {};

	for (const column of table.schema.fields) {
		const columnName = column.name;
		const columnData = [];

		for (let i = 0; i < table.length; i++) {
			if (condition(table, i)) {
				columnData.push(table.getColumn(columnName).get(i));
			}
		}

		const columnVector = table.getColumn(columnName);
		const VectorType = columnVector.constructor;
		filteredData[columnName] = VectorType.from({
			values: columnData,
			type: columnVector.type,
		});
	}

	return Table.new(filteredData);
};

function App({ args }) {
	useEffect(() => {
		Streamlit.setFrameHeight();
	});
	const [tags, setTags] = useState([]);
	const [alertType, setAlertType] = useState([]);
	useEffect(() => {
		const _table = filterTable(data.table, (table, rowIndex) => {
			return (
				tags.includes(table.getColumnAt(3).get(rowIndex)) &&
				alertType.includes(table.getColumnAt(4).get(rowIndex))
			);
		});
		const indexTable = Table.new({
			index: data.table.getColumnAt(0).constructor.from({
				values: Array.from({ length: _table.length }, (_, i) => i),
				type: data.table.getColumnAt(0).type,
			}),
		});
		// const columnTable = Table.new({
		// 	columns: data.columnsTable.getColumnAt(0).constructor.from({
		// 		values: data.columnsTable
		// 			.toArray()
		// 			.map((row) => row[0])
		// 			.slice(1),
		// 		type: data.columnsTable.getColumnAt(0).type,
		// 	}),
		// });
		const arrT = new ArrowTable(
			_table.serialize(),
			indexTable.serialize(),
			data.columnsTable.serialize()
		);
		Streamlit.setComponentValue(arrT);
	}, [tags, alertType]);
	const { data } = args;
	const tagOptions = [...new Set(data.table.getColumnAt(3))];
	const alertTypeOptions = [...new Set(data.table.getColumnAt(4))];
	const handleSelectTags = (selectedTags) => {
		setTags(selectedTags);
	};
	const handleSelectAlertType = (selectedAlertType) => {
		setAlertType(selectedAlertType);
	};

	return (
		<Row gutter={[16, 16]}>
			<Col xs={24}>
				<Typography.Title level={5}>Select tags:</Typography.Title>
				<FilterOptions
					onChange={handleSelectTags}
					options={tagOptions}
					span={6}
				/>
			</Col>
			<Col xs={24}>
				<Typography.Title level={5}>Select type:</Typography.Title>
				<FilterOptions
					onChange={handleSelectAlertType}
					options={alertTypeOptions}
					span={12}
				/>
			</Col>
		</Row>
	);
}

export default withStreamlitConnection(App);

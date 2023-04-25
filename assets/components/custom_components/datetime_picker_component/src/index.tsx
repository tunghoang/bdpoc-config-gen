import { config } from "dotenv";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

config();

// Wrap your CustomDataFrame with the baseui them
createRoot(document.getElementById("root")!).render(
	<React.StrictMode>
		<App />
	</React.StrictMode>
);

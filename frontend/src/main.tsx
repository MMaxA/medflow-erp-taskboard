import React from "react";import ReactDOM from "react-dom/client";import {CssBaseline,ThemeProvider,createTheme} from "@mui/material";import App from "./App";import "./style.css";
const theme=createTheme({palette:{primary:{main:"#24466b"},background:{default:"#f4f6f9"}},shape:{borderRadius:10},typography:{fontFamily:"Inter,Roboto,Arial,sans-serif"}});
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><ThemeProvider theme={theme}><CssBaseline/><App/></ThemeProvider></React.StrictMode>);

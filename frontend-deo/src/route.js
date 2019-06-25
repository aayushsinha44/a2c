import React from 'react';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Index from './views/index/index'

const App2 = () => {
    return (
        <div>Two</div>
    );
};

const RouteList = () => {
    return (
        <Router>
            <div>
            <Route path="/" exact component={Index} />
            <Route path="/two" component={App2} />
            </div>
        </Router>
    );
}

export default RouteList;
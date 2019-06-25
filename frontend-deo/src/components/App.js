import React from 'react';

const App = (props) => {
    console.log(props);
    return (
        <div>{props.data}</div>
    );
};

export default App;
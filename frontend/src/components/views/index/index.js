import React from 'react';
import { BroweserHistory} from 'react-router';

class Index extends React.Component {

    componentDidMount() {
        BroweserHistory.push('/');
    }

    render() {
        return (
            <div>welcome</div>
        );
    }

}

export default Index;
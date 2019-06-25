import React from 'react';
import {Card, Button, Form} from 'semantic-ui-react';

class Index extends React.Component {

    constructor(props) {
        super(props);
        this.state = {username: '', password: ''};
    }


    handleChangeUsername = (event) => {
        this.setState({
            username: event.target.value
        });
    }

    handleChangePassword = (event) => {
        this.setState({
            password: event.target.value
        });
    }

    handleSubmit = (e) => {
        e.preventDefault();
    }

    render() {

        return (
            <Card>
                <Card.Content>
                    <Card.Header>A2C</Card.Header>
                    <Card.Meta>
                        <span className='date'></span>
                    </Card.Meta>
                    <Card.Description>
                        Login
                    </Card.Description>
                    <Card.Content>
                        <Form onSubmit={this.handleSubmit}>
                            <Form.Field>
                                <label>Username</label>
                                <input value={this.state.username} onChange={this.handleChangeUsername} placeholder='username' />
                            </Form.Field>
                            <Form.Field>
                                <label>Password</label>
                                <input type='password' value={this.state.password} onChange={this.handleChangePassword} placeholder='password' />
                            </Form.Field>
                            <Button type='submit'>Submit</Button>
                        </Form>
                    </Card.Content>
                </Card.Content>
            </Card>
        );
    }
}

export default Index;
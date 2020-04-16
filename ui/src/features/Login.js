import React, { Component } from 'react'
import styles from './styles.css'
import backgrpundImage from './backgrpundImage.jpg'
import { } from 'react-router-dom'

export class Login extends Component {

    constructor(props) {
        super(props)
        this.state = {

        }
    }

    handleInputChange = (e) => {
        this.setState({
            [e.target.name]: e.target.value
        });
    }

    handleSubmit = (e) => {
        e.preventDefault();
        this.props.history.push("/gallery");
    }

    render() {
        this.props.history.push("/gallery");
        return (
            <div style={{
                backgroundImage: `url(${backgrpundImage})`
            }} className="container" >
                <div className="overlay" >
                    <form onSubmit={this.handleSubmit} className="login-form" >
                        <div className="notification notification-danger" >
                            You have one notification
                        </div>
                        <div>
                            <label>Email</label>
                            <input onChange={this.handleInputChange} name="email" required type="email" />
                        </div>
                        <div>
                            <label>Password</label>
                            <input onChange={this.handleInputChange} name="password" required type="password" />
                        </div>

                        <button className="button button-primary" >
                            Login
                        </button>

                        <div>
                            <label className="password-forgot-label" >If you've gotten your password, please check your mail box.</label>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

export default Login

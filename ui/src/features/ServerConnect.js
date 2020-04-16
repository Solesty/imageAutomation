import React, { Component } from 'react'
import CONSTANTS from '../features/constants'

export class ServerConnect extends Component {

    constructor(props) {
        super(props)
        this.state = {
            ws: null
        }
    }

    componentDidMount() {
        this.connect();
    }

    timeout = 250;

    connect = () => {
        var ws = new WebSocket(CONSTANTS.WEBSOCKET_URL);
        let that = this; // cache the this
        var connectInterval;

        ws.onopen = () => {
            console.log("connected websocket main component");;

            this.setState({ ws: ws });
            this.timeout = 250; //reset
            clearTimeout(connectInterval); // // clear Interval on on open of websocket connection
        }

        ws.onmessage = (event) => {
            this.props.onMessage(event.data);
        };

        ws.onclose = e => {
            console.log(
                `Socket is closed. Reconnect will be attempted in ${Math.min(
                    10000 / 1000,
                    (that.timeout + that.timeout) / 1000
                )} second.`,
                e.reason
            );
            that.timeout = that.timeout + that.timeout; //increment retry interval
            connectInterval = setTimeout(this.check, Math.min(10000, that.timeout)); //call check function after timeout
        }

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );

            ws.close();
        };


    }

    /**
        * utilited by the @function connect to check if the connection is close, if so attempts to reconnect
        */
    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState == WebSocket.CLOSED) this.connect(); //check if websocket instance is closed, if so call `connect` function.
    };
    render() {
        return (
            <div>

            </div>
        )
    }
}

export default ServerConnect

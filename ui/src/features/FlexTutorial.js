import React, { Component } from 'react'
import styles from './flexTuts.css'

export class FlexTutorial extends Component {

    constructor(props) {
        super(props)
        this.state = {

        }
    }

    render() {
        return (
            <div>
                <div className="container-1" >
                    <div className="box-1">
                        <h3>Box One</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="box-2">
                        <h3>Box Two</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="box-3">
                        <h3>Box Three</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                </div>

                <div className="container-2" >
                    <div className="container-2-box">
                        <h3>Box One</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="container-2-box">
                        <h3>Box Two</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="container-2-box">
                        <h3>Box Three</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                </div>

                <div className="container-3" >
                    <div className="container-3-box">
                        <h3>Box One</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="container-3-box">
                        <h3>Box Two</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                    <div className="container-3-box">
                        <h3>Box Three</h3>
                        <p>Lorem ipsum dcolor sit, amet, consectour adipiscing olit.</p>
                    </div>

                </div>
            </div>
        )
    }
}

export default FlexTutorial

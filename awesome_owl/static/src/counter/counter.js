/** @odoo-module **/

import { Component, useState  } from "@odoo/owl";

export class Counter extends Component {
    static template = "awesome_owl.Counter";
	
	reset_to_zero() {
		this.state.value = 1;
	}
	
	setup() {
		this.state = useState({value:1});
	}
	
	increment() {
        this.state.value++;
    }
}

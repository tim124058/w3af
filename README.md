## w3af - Web Application Attack and Audit Framework

w3af is an [open source](https://www.gnu.org/licenses/gpl-2.0.txt) web 
application security scanner which helps developers and penetration testers
identify and exploit vulnerabilities in their web applications.

The scanner is able to identify [200+ vulnerabilities](https://github.com/andresriancho/w3af/blob/master/w3af/core/data/constants/vulns.py),
including [Cross-Site Scripting](https://github.com/andresriancho/w3af/blob/master/w3af/plugins/audit/xss.py),
[SQL injection](https://github.com/andresriancho/w3af/blob/master/w3af/plugins/audit/sqli.py) and
[OS commanding](https://github.com/andresriancho/w3af/blob/master/w3af/plugins/audit/os_commanding.py).

## Contributing

Pull requests are always welcome! If you're not sure where to start, please take
a look at the [First steps as a contributor](https://github.com/andresriancho/w3af/wiki/First-steps-as-a-contributor)
document in our wiki. All contributions, no matter how small, are welcome.

## Links and documentation
 * [w3af's main site](http://w3af.org/)
 * [Project documentation](http://docs.w3af.org/en/latest/)

## Sponsor the project

Found this project useful? Donations are accepted via [ethereum](https://www.ethereum.org/) at `0xb1B56F04E6cc5F4ACcB19678959800824DA8DE82`

## Kali install

Install:

```shell
$ git clone https://github.com/tim124058/w3af.git
$ cd w3af
$ ./kali_install.sh
```

Run with gui:

```shell
$ w3af_gui
```

reference : [https://blog.csdn.net/weixin_37224075/article/details/78215791](https://blog.csdn.net/weixin_37224075/article/details/78215791)

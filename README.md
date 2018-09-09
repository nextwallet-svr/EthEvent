########################################
# EthEvent
########################################

## 接口
```
1. 注册event名字及其处理函数
regEventHandler(event_name, handler)
handler是event对应的处理函数，其参数必须是(contract, event):
contract: 
通过web3.eth.contract(address=contract_address, abi=abi)创建的contract对象

event:
通过filter.get_new_entries()/get_all_entries()获得的event列表中一个元素

2. 创建event filter
createEventFilters(_abi, from_block, to_block = 0, confirm_block_num = 0)

3. 销毁event filter
destroyEventFilters()
如果创建latest filter，则不必销毁，filter可以重用，在进程loop中循环调用
如果创建指定fromBlock/toBlock的filter，则需要销毁，避免filter泄漏

4. 执行event处理函数
callEventHandlers(_abi)
可以在进程loop中调用

```

## 示例
```
#用户实现EventCreate的处理函数
def event_create_handler(contract, event):
    pass

#用户调用注册event及其处理函数
def regUserEventHandlers():
    regEventHandler("EventCreate", event_create_handler)

#创建1
#用户调用创建event filter (latest)，并在loop中接收和处理event
def main_loop_1():
    regUserEventHandlers()
    createEventFilters(getAbi(), 'latest')
    while True:
        try:
            callEventHandlers(getAbi())
        except Exception as e:
            error('event filte loop fail, e: %s', e)
        time.sleep(1)

#创建2
#用户调用创建event filter (指定from，to block, confirm_block_num)，并在loop中接收和处理event
def main_loop_2():
    regUserEventHandlers()
    while True:
        try:
            from_block = web3.eth.blockNumber
            createEventFilters(getAbi(), from_block, confirm_block_num=15)
            callEventHandlers(getAbi())
            destroyEventFilters()
        except Exception as e:
            error('event filte loop fail, e: %s', e)
        time.sleep(1)
```

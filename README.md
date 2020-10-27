
## 简介

一个运行的执行最终会到达如下的一种状态：
1. 执行成功。
2. 某些步骤出错，执行失败。
3. 执行时间超过流程定义的超时时间，执行超时失败。
4. 调用StopExecution API手工停止执行。

当流程执行结束时，Serverless工作流服务会取消正在执行的函数。本示例演示如何在取消函数执行后执行一些后续其它操作。

## 工作原理

在调用StopExecution结束某一流程执行时，一个正在被结束的执行不应该再执行其它操作，因此没有机会在该流程中执行其它操作。但是，我们仍然可以结合Serverless工作流的子流程功能来做一些后期处理。

1. 在主流程中同步启动子流程执行，对子流程的特定错误进行处理。
2. 子流程负责编排真正的业务函数。
3. 当需要停止业务函数执行时，调用API停止子流程执行，指定错误原因。
4. 当子流程执行结束后，主流程会捕获步骤3指定的错误原因，执行相应处理。

## 使用步骤

1. 部署示例
```
fun deploy
```

2. 启动主流程
```
aliyun fnf StartExecution --FlowName post-actions-flow --Input '{"subflowExecName":"run10", "subflowInput":"test"}' --ExecutionName main1
{
        "FlowDefinition": "version: v1\ntype: flow\nsteps:\n  - type: task\n    name: startChildFlow\n    resourceArn: 'acs:fnf:::flow/post-actions-subflow'\n    pattern: sync\n    inputMappings:\n      - target: subflowInput\n        source: $input.subflowInput\n      - target: subflowExecName\n        source: $input.subflowExecName\n    serviceParams:\n      Input: $\n      ExecutionName: $.subflowExecName\n    catch:\n      - errors:\n          - AnyCustomError\n        goto: postAction\n  - type: pass\n    name: final\n    end: true\n  - type: pass\n    name: postAction\n",
        "FlowName": "post-actions-flow",
        "Input": "{\"subflowExecName\":\"run10\", \"subflowInput\":\"test\"}",
        "Name": "main1",
        "Output": "",
        "RequestId": "52ef0076-da4e-0c2c-f434-5f0cfbb2f193",
        "StartedTime": "2020-10-27T22:17:52.413Z",
        "Status": "",
        "StoppedTime": ""
}
```

3. 停止子流程。注意，指定Error为AnyCustomError，该Error和主流程中的捕获的Error保持一致。
```
aliyun fnf StopExecution --FlowName post-actions-subflow --ExecutionName run10 --Error AnyCustomError
{
        "FlowDefinition": "version: v1\ntype: flow\nsteps:\n  - type: task\n    name: longRunning\n    resourceArn: 'acs:fc:::services/post-actions-service/functions/long-running'\n",
        "FlowName": "post-actions-subflow",
        "Input": "{\"subflowExecName\":\"run10\",\"subflowInput\":\"test\"}",
        "Name": "run10",
        "Output": "",
        "RequestId": "a065b040-317e-1f5e-9326-bac61e359657",
        "StartedTime": "2020-10-27T22:17:53.491Z",
        "Status": "Running",
        "StoppedTime": "2020-10-27T22:18:15.009Z"
}
```

4. 查看子流程执行
```
aliyun fnf DescribeExecution --FlowName post-actions-subflow --ExecutionName run10
{
        "FlowDefinition": "version: v1\ntype: flow\nsteps:\n  - type: task\n    name: longRunning\n    resourceArn: 'acs:fc:::services/post-actions-service/functions/long-running'\n",
        "FlowName": "post-actions-subflow",
        "Input": "{\"subflowExecName\":\"run10\",\"subflowInput\":\"test\"}",
        "Name": "run10",
        "Output": "",
        "RequestId": "e075f3f4-3ad0-e694-5134-a10a7a46d2c6",
        "StartedTime": "2020-10-27T22:17:53.491Z",
        "Status": "Stopped",
        "StoppedTime": "2020-10-27T22:18:15.009Z"
}
```
5. 查看主流程执行
```
aliyun fnf DescribeExecution --FlowName post-actions-flow --ExecutionName main1
{
        "FlowDefinition": "version: v1\ntype: flow\nsteps:\n  - type: task\n    name: startChildFlow\n    resourceArn: 'acs:fnf:::flow/post-actions-subflow'\n    pattern: sync\n    inputMappings:\n      - target: subflowInput\n        source: $input.subflowInput\n      - target: subflowExecName\n        source: $input.subflowExecName\n    serviceParams:\n      Input: $\n      ExecutionName: $.subflowExecName\n    catch:\n      - errors:\n          - AnyCustomError\n        goto: postAction\n  - type: pass\n    name: final\n    end: true\n  - type: pass\n    name: postAction\n",
        "FlowName": "post-actions-flow",
        "Input": "{\"subflowExecName\":\"run10\", \"subflowInput\":\"test\"}",
        "Name": "main2",
        "Output": "{}",
        "RequestId": "63bf66b4-49e6-f50e-d3ee-3cb250cb1cf7",
        "StartedTime": "2020-10-27T22:22:34.484Z",
        "Status": "Succeeded",
        "StoppedTime": "2020-10-27T22:23:08.771Z"
}
```
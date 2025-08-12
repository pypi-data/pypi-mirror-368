- ✅ typing，希望可以可以使用typing方法，例如AutoCRUD[XXX]來指定這個crud的resource type
- ✅ use_plural應該也能在autocrud init時給
- ✅ 允許api background task，也許放在RouteConfig裡面，也許RouteConfig的attribute type不應該是bool，讓我們能更細緻的調整每個route的行為
- ✅ 支援get model by model class而不是只能access by resource name，也要注意一個model註冊兩次(resource name不同)的話，用這樣的方式access時要跳錯
- ✅ 讓我們統一backgroun task的callback signature，只收一個input，就是該router的output (不是response object，完全就是那個router function的output)，所以我們甚至可以使用一些手法讓所有router (get/update/create/delete/...)都套用同一個bgtask邏輯
- ✅ 可以支援plugin其他種類的route，我們需要定義plugin的interface，user可以實作並透過我們的方法注入到我們的系統中，接著在autogen routes時，也跑他的東西。
  1. 第一先讓我們自己的route都符合該設計好的interface
  2. 我們自己的route都以default注入的形式進入我們的系統
  3. 讓user也能注入他們的route
